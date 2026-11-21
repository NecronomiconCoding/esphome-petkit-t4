"""Replay ESP-IDF's early-boot reserved-memory validation (memory_layout_utils.c:
s_prepare_reserved_regions) against a firmware.elf, plus linker-script/sdkconfig consistency."""
import struct, subprocess, sys, re, os
TC=os.path.expanduser('~/.platformio/packages/toolchain-xtensa-esp-elf/bin/xtensa-esp-elf-')
def check(build):
    env=build+'/.pioenvs/petkit-t4'; elf=env+'/firmware.elf'
    nm=subprocess.run([TC+'nm',elf],capture_output=True,text=True,check=True).stdout
    sym={l.split()[2]:int(l.split()[0],16) for l in nm.splitlines() if len(l.split())==3}
    a,b=sym['soc_reserved_memory_region_start'],sym['soc_reserved_memory_region_end']
    data=open(elf,'rb').read()
    # locate via program headers
    e_phoff,=struct.unpack_from('<I',data,28); e_phentsize,e_phnum=struct.unpack_from('<HH',data,42)
    raw=None
    for i in range(e_phnum):
        p_type,p_offset,p_vaddr,p_paddr,p_filesz,p_memsz,p_flags,p_align=struct.unpack_from('<8I',data,e_phoff+i*e_phentsize)
        if p_type==1 and p_vaddr<=a and b<=p_vaddr+p_filesz: raw=data[p_offset+(a-p_vaddr):p_offset+(b-p_vaddr)]
    assert raw is not None and len(raw)%8==0
    regs=sorted(struct.unpack_from('<II',raw,i) for i in range(0,len(raw),8))
    ok=True; msgs=[]
    # IDF word-aligns each region and requires start <= end before comparing neighbours.
    regs=[(s_ & ~3, (e_ + 3) & ~3) for s_,e_ in regs]
    for s_,e_ in regs:
        if s_>e_: ok=False; msgs.append(f'BAD REGION: start {s_:#x} > end {e_:#x}')
    binp=env+'/firmware.bin'
    if os.path.exists(binp) and os.path.getsize(binp)>0x3C0000: ok=False; msgs.append('IMAGE LARGER THAN APP PARTITION')
    if os.path.getmtime(elf) < os.path.getmtime(env+'/memory.ld')-1: ok=False; msgs.append('ELF older than linker script')
    for i in range(len(regs)-1):
        if not regs[i+1][0]>regs[i][0]: ok=False; msgs.append(f'ASSERT start: {regs[i+1][0]:#x} !> {regs[i][0]:#x}')
        if regs[i][1]>regs[i+1][0]: ok=False; msgs.append(f'OVERLAP: [{regs[i][0]:#x},{regs[i][1]:#x}) vs [{regs[i+1][0]:#x},...)')
    sdk=open(build+'/sdkconfig.petkit-t4').read()
    m=re.search(r'^CONFIG_BTDM_RESERVE_DRAM=(\S+)',sdk,re.M); want=int(m.group(1),16) if m else 0
    ld=re.search(r'dram0_0_seg \(RW\) : org = 0x3FFB0000 \+ (\S+),',open(env+'/memory.ld').read()).group(1)
    got=int(ld,16) if ld.startswith('0x') else int(ld)
    if got!=want: ok=False; msgs.append(f'STALE LINKER SCRIPT: memory.ld reserve {got:#x} != sdkconfig {want:#x}')
    if not (0x3FFB0000+want <= sym['_data_start'] < 0x3FFB0000+want+16): ok=False; msgs.append(f"_data_start {sym['_data_start']:#x} != {0x3FFB0000+want:#x}")
    return ok,len(regs),msgs
if __name__=='__main__':
    rc=0
    for b in sys.argv[1:]:
        ok,n,msgs=check(b); print(('PASS' if ok else 'FAIL'),b.split('/scratchpad/')[-1].split('/Downloads/')[-1][:60],f'({n} regions)',*msgs,sep='  ')
        rc|=0 if ok else 1
    sys.exit(rc)
