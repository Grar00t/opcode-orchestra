#!/usr/bin/env python3
"""Execute assembled x86 with scripted I/O. NOT a DOS/peripheral emulator.

Optional dependency: unicorn==2.1.4. Missing tools fail, never count as a pass.
OO_TEST_ROOT selects an original source tree for differential regressions.
"""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest
import struct
import unicorn as uc
from unicorn import x86_const as x

ROOT = Path(os.environ.get('OO_TEST_ROOT', Path(__file__).resolve().parents[1]))
NASM = os.environ.get('NASM', 'nasm')
BASE = 0x10000

class Machine:
    def __init__(self, includes, body, suffix='', program=None):
        if not shutil.which(NASM):
            raise RuntimeError('NASM executable missing')
        if program:
            source = (ROOT/program).read_text(encoding='utf-8')
        else:
            source = 'BITS 16\nORG 100h\njmp __test_entry\n'
            source += ''.join(f'%include "{name}"\n' for name in includes)
        source += '\n__test_entry:\n' + body + '\n__test_halt:\nhlt\n' + suffix
        source += '\ndw __test_entry, __test_halt\n'
        with tempfile.TemporaryDirectory(prefix='oo-cpu-') as tmp:
            asm = Path(tmp)/'test.asm'; out = Path(tmp)/'test.bin'
            asm.write_text(source, encoding='utf-8')
            result = subprocess.run([NASM,'-w+all','-Werror','-w-reloc-abs-word','-I',str(ROOT/'engine')+'/',
                                     '-I',str(ROOT/'documentary')+'/', '-f','bin',str(asm),'-o',str(out)], capture_output=True, timeout=20)
            if result.returncode:
                raise RuntimeError(result.stderr.decode())
            self.code = out.read_bytes()
        self.entry, halt = struct.unpack('<HH', self.code[-4:])
        self.m = uc.Uc(uc.UC_ARCH_X86, uc.UC_MODE_16)
        self.m.mem_map(0, 0x200000)
        self.m.mem_write(BASE+0x100, self.code)
        for reg,value in ((x.UC_X86_REG_CS,0x1000),(x.UC_X86_REG_DS,0x1000),
                          (x.UC_X86_REG_SS,0x7000),(x.UC_X86_REG_SP,0xfffe),
                          (x.UC_X86_REG_ES,0xa000),(x.UC_X86_REG_EFLAGS,0x202)):
            self.m.reg_write(reg,value)
        self.ports = []
        self.outputs = {}
        self.halted = False
        self.input = lambda port: 0
        self.interrupt = self.unexpected_interrupt
        self.output = lambda port, value: None
        self.m.hook_add(uc.UC_HOOK_INSN, self.read_port, None, 1, 0, x.UC_X86_INS_IN)
        self.m.hook_add(uc.UC_HOOK_INSN, self.write_port, None, 1, 0, x.UC_X86_INS_OUT)
        self.m.hook_add(uc.UC_HOOK_INTR, lambda m,n,u: self.interrupt(n))
        self.m.hook_add(uc.UC_HOOK_CODE, self.trace, None, BASE+halt, BASE+halt)
    def unexpected_interrupt(self, number):
        raise AssertionError(f'unexpected interrupt {number:02x}')
    def read_port(self, m, port, size, user):
        value = self.input(port)
        self.ports.append(('in',port,value))
        return value
    def write_port(self, m, port, size, value, user):
        self.ports.append(('out',port,value))
        self.outputs.setdefault(port, []).append(value)
        self.output(port,value)
    def trace(self, m, address, size, user):
        if m.mem_read(address,1) == b'\xf4':
            self.halted = True
    def run(self, count=200000):
        self.m.emu_start(BASE+self.entry, BASE+0x100+len(self.code), count=count)
        return self
    @property
    def carry(self):
        return self.m.reg_read(x.UC_X86_REG_EFLAGS) & 1

class SBModel:
    """Scripted SB16 ready/reset/version/IRQ routing, not a peripheral emulator."""
    def __init__(self, q, complete=True, irq_config=4, fail_command=None):
        self.q=q; self.complete=complete; self.irq_config=irq_config
        self.fail_command=fail_command; self.fail_active=False
        self.pic=0xa5; self.mixer=0; self.queue=[]; self.pending=False
        self.vector=(0x1234,0xf000); self.original_vector=self.vector
        self.vector_updates=[]; self.pit=0xfffe; self.pit_low=True
        self.injections=0
        q.input=self.read; q.output=self.write; q.interrupt=self.interrupt
        q.m.hook_add(uc.UC_HOOK_CODE,self.deliver)
        q.m.hook_add(uc.UC_HOOK_MEM_READ,self.tick,None,0x46c,0x46f)
        self.ticks=0
    def read(self, port):
        if port==0x40:
            if self.pit_low:
                self.pit=(self.pit-4)&0xffff; value=self.pit&255
            else: value=self.pit>>8
            self.pit_low=not self.pit_low
            return value
        if port==0x21:return self.pic
        if port==0x225:return {0x80:self.irq_config,0x81:2,0x82:1}.get(self.mixer,0)
        if port==0x22e:return 0x80 if self.queue else 0
        if port==0x22a:return self.queue.pop(0) if self.queue else 0
        if port==0x22c and self.fail_active:
            self.q.m.reg_write(x.UC_X86_REG_CX,1)
            return 0x80
        return 0
    def write(self, port, value):
        if port==0x21:self.pic=value
        elif port==0x224:self.mixer=value
        elif port==0x226 and value==0:
            self.queue=[0xaa];self.fail_active=False
        elif port==0x22c:
            if value==0xe1:self.queue=[4,5]
            if value==self.fail_command:self.fail_active=True
            if self.q.outputs[port][-5:]==[0x40,131,0x14,15,0] and self.complete:
                self.pending=True
    def interrupt(self, number):
        if number!=0x21:raise AssertionError(f'unexpected INT {number}')
        ah=self.q.m.reg_read(x.UC_X86_REG_AH)
        if ah==0x35:
            self.q.m.reg_write(x.UC_X86_REG_BX,self.vector[0])
            self.q.m.reg_write(x.UC_X86_REG_ES,self.vector[1])
        elif ah==0x25:
            self.vector=(self.q.m.reg_read(x.UC_X86_REG_DX),self.q.m.reg_read(x.UC_X86_REG_DS))
            self.vector_updates.append(self.vector)
        else:raise AssertionError(f'unexpected DOS AH={ah}')
    def deliver(self,m,address,size,user):
        if not self.pending:return
        flags=m.reg_read(x.UC_X86_REG_EFLAGS)
        if not(flags&0x200):return
        self.pending=False; self.injections+=1
        sp=(m.reg_read(x.UC_X86_REG_SP)-6)&0xffff
        stack=m.reg_read(x.UC_X86_REG_SS)*16+sp
        m.mem_write(stack,struct.pack('<HHH',m.reg_read(x.UC_X86_REG_IP),m.reg_read(x.UC_X86_REG_CS),flags&0xffff))
        m.reg_write(x.UC_X86_REG_SP,sp)
        m.reg_write(x.UC_X86_REG_EFLAGS,flags&~0x300)
        m.reg_write(x.UC_X86_REG_CS,self.vector[1]);m.reg_write(x.UC_X86_REG_IP,self.vector[0])
    def tick(self,m,access,address,size,value,user):
        if address==0x46c:
            self.ticks=(self.ticks+100)%0x1800b0
            m.mem_write(0x46c,struct.pack('<I',self.ticks))

class CPUContracts(unittest.TestCase):
    def test_vga_hline_right_bottom_guard(self):
        q = Machine(['vga13.inc'], 'mov ax,319\nmov bx,199\nmov cx,65535\nmov dl,7\ncall vga_hline')
        q.m.mem_write(0xa0000, b'\xcc'*65536)
        q.run()
        self.assertTrue(q.halted)
        self.assertEqual(q.m.mem_read(0xa0000+63999,1),b'\x07')
        self.assertEqual(q.m.mem_read(0xa0000+64000,1536), b'\xcc'*1536)
        self.assertEqual(q.m.mem_read(0xa0000,63999), b'\xcc'*63999)
        self.assertEqual(q.m.reg_read(x.UC_X86_REG_SP),0xfffe)
    def test_wait_cs_full_minute_terminates(self):
        q = Machine(['opl2.inc'], 'mov cx,6000\ncall wait_cs')
        calls = 0
        def clock(number):
            nonlocal calls
            self.assertEqual(number,0x21)
            self.assertEqual(q.m.reg_read(x.UC_X86_REG_AH),0x2c)
            q.m.reg_write(x.UC_X86_REG_DX, ((calls % 60) << 8))
            calls += 1
        q.interrupt = clock
        q.run(100000)
        self.assertTrue(q.halted, f'wait never returned; {calls} clock observations')
        self.assertEqual(calls,61)
        self.assertEqual(q.m.reg_read(x.UC_X86_REG_CX),6000)
        self.assertEqual(q.m.reg_read(x.UC_X86_REG_SP),0xfffe)
    def test_pcm_last_dsp_byte_failure_is_not_success(self):
        q = Machine(['sbpcm.inc'], 'mov si,5000h\nmov cx,16\n%ifdef SB_HAS_LIFECYCLE\ncall sb_pcm_start\n%else\ncall sb_pcm_play\n%endif')
        # Original start-only interface: force a timeout on the final DSP byte.
        def dsp(port):
            sent = q.outputs.get(0x22c, [])
            if port == 0x22c and len(sent) >= 4:
                q.m.reg_write(x.UC_X86_REG_CX, 1) # last bounded-poll iteration
                return 0x80
            return 0
        q.input = dsp
        q.run(1000000)
        self.assertTrue(q.halted)
        self.assertEqual(q.carry,1)
        masks=[v for d,p,v in q.ports if d=='out' and p==0x0a]
        self.assertEqual(masks[-1],5, 'failed PCM setup left DMA unmasked')

    def test_documentary_spectrum_preserves_frame_counter(self):
        q=Machine([], 'mov bp,7\nmov word [scene_phase],6\ncall draw_spectrum_frame',
                  program='showcase/documentary.asm').run(2000000)
        self.assertTrue(q.halted)
        self.assertEqual(q.m.reg_read(x.UC_X86_REG_BP),7)
        self.assertEqual(q.m.reg_read(x.UC_X86_REG_SP),0xfffe)
    def test_font_and_rectangle_coordinates_do_not_wrap(self):
        for body in ('mov al,65\nmov bx,65535\nmov dx,65535\nmov cx,0xff07\ncall vga_draw_char5x7',
                     'mov ax,319\nmov bx,199\nmov cx,65535\nmov si,65535\nmov dl,7\ncall cinema_fill_rect'):
            with self.subTest(body=body):
                q=Machine(['vga13.inc','font5x7.inc','cinematic.inc'],body)
                q.m.mem_write(0xa0000+64000,b'G'*1536)
                q.run(300000)
                self.assertTrue(q.halted)
                self.assertEqual(q.m.mem_read(0xa0000+64000,1536),b'G'*1536)
    def test_speaker_division_rejects_low_frequency(self):
        q=Machine(['pcspeaker.inc'],'mov bx,1\nmov cx,0\ncall play_note').run()
        self.assertTrue(q.halted);self.assertEqual(q.carry,1);self.assertEqual(q.ports,[])
    def test_instrument_preserves_opl3_pan(self):
        q=Machine(['opl2.inc','instruments.inc','opl3.inc'],
                  'mov byte [opl_kind],3\ncall opl3_enable\ncall opl3_stereo_default\nmov al,2\ncall instrument_select').run()
        registers={};reg=0
        for direction,port,value in q.ports:
            if direction=='out' and port==0x388:reg=value
            if direction=='out' and port==0x389:registers[reg]=value
        self.assertEqual([registers[c]&0x30 for c in (0xc0,0xc1,0xc2)],[0x10,0x30,0x20])
    def test_opl_invalid_arguments_do_not_write(self):
        for body in ('mov ax,1024\ncall opl_key_on','mov al,4\ncall instrument_select',
                     'mov byte [opl3_active],1\nmov dl,9\nmov bl,16\nmov cl,4\ncall opl3_set_pan'):
            with self.subTest(body=body):
                q=Machine(['opl2.inc','instruments.inc','opl3.inc'],body).run()
                self.assertEqual(q.carry,1);self.assertEqual(q.ports,[])
    def test_opl_shutdown_clears_both_banks_before_mode(self):
        q=Machine(['opl2.inc'],'mov byte [opl_kind],3\ncall opl_shutdown').run()
        writes={};address={}
        for d,p,v in q.ports:
            if d!='out':continue
            if p in (0x388,0x38a):address[p]=v
            elif p in (0x389,0x38b):writes[(p-1,address[p-1])]=v
        for bank in (0x388,0x38a):
            for channel in range(9):self.assertEqual(writes[bank,0xb0+channel],0)
        self.assertEqual(writes[0x38a,4],0);self.assertEqual(writes[0x38a,5],0)
    def test_opl_write_delays_and_register_preservation(self):
        q=Machine(['opl2.inc'],'mov ax,20h\nmov bx,1234h\nmov cx,5678h\nmov dx,9abch\ncall opl_write').run()
        self.assertEqual(q.ports,[('out',0x388,0x20)]+[('in',0x388,0)]*6+
                         [('out',0x389,0x34)]+[('in',0x388,0)]*35)
        for reg,value in ((x.UC_X86_REG_AX,0x20),(x.UC_X86_REG_BX,0x1234),(x.UC_X86_REG_CX,0x5678),(x.UC_X86_REG_DX,0x9abc)):
            self.assertEqual(q.m.reg_read(reg),value)
    def test_media_truncations_and_unknown_opcode_fail(self):
        valid=bytes([4])+struct.pack('<HHHHB',319,199,65535,65535,7)+bytes([0])
        variants=[valid[:n] for n in range(len(valid))]+[b'\xff',b'\0\0']
        for data in variants:
            with self.subTest(data=data.hex()):
                suffix='stream: db '+','.join(map(str,data))+'\nendstream:\n' if data else 'stream:\nendstream:\n'
                q=Machine(['vga13.inc','font5x7.inc','media_ops.inc'],
                          'mov si,stream\nmov di,endstream\ncall media_execute',suffix).run()
                self.assertTrue(q.halted);self.assertEqual(q.carry,1)
    def test_vga_restores_mode_page_and_es(self):
        q=Machine(['vga13.inc'],'call vga_mode13\ncall vga_text_mode')
        mode=7;page=2
        q.m.reg_write(x.UC_X86_REG_ES,0x1234)
        def video(n):
            nonlocal mode,page
            self.assertEqual(n,0x10)
            ah=q.m.reg_read(x.UC_X86_REG_AH);al=q.m.reg_read(x.UC_X86_REG_AL)
            if ah==0x0f:q.m.reg_write(x.UC_X86_REG_AL,mode);q.m.reg_write(x.UC_X86_REG_BH,page)
            elif ah==0:mode=al
            elif ah==5:page=al
            else:raise AssertionError(ah)
        q.interrupt=video;q.run()
        self.assertEqual((mode,page),(7,2));self.assertEqual(q.m.reg_read(x.UC_X86_REG_ES),0x1234)
    def test_pcm_programs_address_page_count_and_mode(self):
        q=Machine(['sbpcm.inc'],'mov si,5000h\nmov cx,16\ncall sb_pcm_start').run()
        self.assertEqual(q.carry,0)
        self.assertEqual(q.outputs[2],[0,0x50]);self.assertEqual(q.outputs[0x83],[1])
        self.assertEqual(q.outputs[3],[15,0]);self.assertEqual(q.outputs[0x0b],[0x49])
        self.assertEqual(q.outputs[0x22c],[0x40,131,0x14,15,0])
    def test_pcm_boundary_rejected_before_hardware(self):
        q=Machine(['sbpcm.inc'],'mov si,0fff0h\nmov cx,17\ncall sb_pcm_play').run()
        self.assertEqual(q.carry,1);self.assertEqual(q.ports,[])
    def test_pcm_full_lifecycle_restores_vector_pic_and_stack(self):
        q=Machine(['sbpcm.inc'],'mov si,5000h\nmov cx,16\ncall sb_pcm_play')
        model=SBModel(q);q.run(100000)
        self.assertTrue(q.halted);self.assertEqual(q.carry,0)
        self.assertEqual(model.injections,1);self.assertEqual(model.vector,model.original_vector)
        self.assertEqual(model.pic,0xa5);self.assertEqual(len(model.vector_updates),2)
        self.assertEqual(q.outputs[0x0a][-1],5);self.assertEqual(q.outputs[0x22c][-1],0xd3)
        self.assertIn(('out',0x20,0x20),q.ports)
        eoi=q.ports.index(('out',0x20,0x20))
        self.assertEqual(q.ports[eoi-1][0:2],('in',0x22e))
        self.assertEqual(q.m.reg_read(x.UC_X86_REG_SP),0xfffe)
        self.assertEqual(q.m.reg_read(x.UC_X86_REG_DS),0x1000)
        self.assertEqual(q.m.reg_read(x.UC_X86_REG_ES),0xa000)
        self.assertTrue(q.m.reg_read(x.UC_X86_REG_EFLAGS)&0x200)
    def test_pcm_failure_and_timeout_cleanup(self):
        for options in ({'complete':False},{'fail_command':0x14}):
            with self.subTest(options=options):
                q=Machine(['sbpcm.inc'],'mov si,5000h\nmov cx,16\ncall sb_pcm_play')
                model=SBModel(q,**options);q.run(100000)
                self.assertTrue(q.halted);self.assertEqual(q.carry,1)
                self.assertEqual(model.vector,model.original_vector);self.assertEqual(model.pic,0xa5)
                self.assertEqual(q.outputs[0x0a][-1],5)
    def test_pcm_unsupported_irq_never_programs_dma(self):
        q=Machine(['sbpcm.inc'],'mov si,5000h\nmov cx,16\ncall sb_pcm_play')
        model=SBModel(q,irq_config=2);q.run()
        self.assertEqual(q.carry,1);self.assertNotIn(0x0a,q.outputs)
        self.assertEqual(model.vector_updates,[])

    def test_vga_bulk_primitives_preserve_direction_flag(self):
        for body in ('mov al,7\ncall vga_clear', 'mov ax,0\nmov bx,0\nmov cx,5\nmov dl,7\ncall vga_hline'):
            q=Machine(['vga13.inc'],'std\n'+body).run()
            self.assertTrue(q.halted)
            self.assertTrue(q.m.reg_read(x.UC_X86_REG_EFLAGS)&0x400)
            self.assertEqual(q.m.reg_read(x.UC_X86_REG_SP),0xfffe)

    def test_speaker_wait_handles_midnight_without_consuming_flag(self):
        q=Machine(['pcspeaker.inc'],'mov cx,3\ncall wait_ticks')
        ticks=iter([0x1800ae,0x1800af,0,1,2])
        reads=[]
        def tick(m,access,address,size,value,user):
            if address==0x46c:
                value=next(ticks);reads.append(value)
                m.mem_write(0x46c,struct.pack('<I',value))
        q.m.mem_write(0x470,b'\x01')
        q.m.hook_add(uc.UC_HOOK_MEM_READ,tick,None,0x46c,0x46f)
        q.run()
        self.assertTrue(q.halted);self.assertEqual(len(reads),4)
        self.assertEqual(q.m.mem_read(0x470,1),b'\x01')
        self.assertEqual(q.m.reg_read(x.UC_X86_REG_CX),3)

    def test_opl_capability_detection_scripted_status(self):
        for signature, timer_ok, expected in ((6,True,2),(0,True,3),(255,False,0),(2,True,0),(6,False,0)):
            with self.subTest(signature=signature,timer_ok=timer_ok):
                q=Machine(['opl2.inc'],'call opl_detect')
                register=0;running=False;pit=0xfffe;low=True
                def output(port,value):
                    nonlocal register,running
                    if port==0x388:register=value
                    if port==0x389 and register==4:running=value==0x21
                def input_port(port):
                    nonlocal pit,low
                    if port==0x40:
                        if low:pit=(pit-4)&65535
                        value=(pit&255) if low else (pit>>8)
                        low=not low
                        return value
                    if port==0x388:return signature | (0xc0 if running and timer_ok else 0)
                    return 0
                q.output=output;q.input=input_port;q.run(100000)
                self.assertTrue(q.halted)
                self.assertEqual(q.m.reg_read(x.UC_X86_REG_AL),expected)
                self.assertEqual(q.carry,int(expected==0))
                self.assertFalse(running)

    def test_pit_delay_stall_fails_with_balanced_stack(self):
        q=Machine(['isa_delay.inc'],'mov cx,8\ncall isa_delay_min').run(3000000)
        self.assertTrue(q.halted);self.assertEqual(q.carry,1)
        self.assertEqual(q.m.reg_read(x.UC_X86_REG_SP),0xfffe)
        self.assertTrue(q.m.reg_read(x.UC_X86_REG_EFLAGS)&0x200)

    def test_unsupported_drum_and_four_op_arguments(self):
        for body in ('mov al,32\ncall opl_drum_hit','mov byte [opl3_active],1\nmov ax,1024\ncall opl3_4op_key_on'):
            q=Machine(['opl2.inc','opl3.inc','percussion.inc'],body).run()
            self.assertTrue(q.halted);self.assertEqual(q.carry,1);self.assertEqual(q.ports,[])

if __name__ == '__main__':
    unittest.main(verbosity=2)
