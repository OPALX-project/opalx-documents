from pathlib import Path
for name in ['FFT2D5FieldStorage.h','FFT2D5FieldStorage.cpp']:
 p=Path('src/SpaceCharge/FFT2D5')/name;s=p.read_text();lines=s.splitlines(True);result=[];stack=[];active=True
 for line in lines:
  if line.startswith('#if ') and 'OPALX_FFT2D5_ALGORITHM_USE_IPPL_2D_POISSON_SOLVER' in line:
   yes='!' in line;stack.append((active,yes));active=active and yes;continue
  if stack and line.startswith('#else'):
   parent,yes=stack[-1];active=parent and not yes;continue
  if stack and line.startswith('#endif'):
   active=stack.pop()[0];continue
  if active:result.append(line)
 s=''.join(result)
 if name.endswith('.h'):
  a=s.index('// The native solver integrates');b=s.index('namespace opalx::spacecharge',a);s=s[:a]+s[b:]
  s='\n'.join(l for l in s.split('\n') if 'using OpenSolver2 ' not in l and 'solverParameters_m' not in l)
 else:
  s='\n'.join(l for l in s.split('\n') if 'solverParameters_m.add(' not in l)
 s=s.replace('solver2','solver');p.write_text(s)
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Algorithm.h');s=p.read_text();s='\n'.join(l for l in s.split('\n') if 'using OpenSolver2D_t' not in l);p.write_text(s)
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Algorithm.hpp');s=p.read_text();a=s.index('            // Scalar form retained');b=s.index('            /** One league entry',a);s=s[:a]+s[b:];s=s.replace(' * @brief Numerical routines retained from master a5c859240, PartBunch/Solve2d5.hpp.\n *\n * Arithmetic, interpolation, field signs, stage ordering, and diagnostic hooks are retained.\n * Integration changes replace PartBunch access with borrowed containers and per-call state,\n * redirect workspace access, select tracking-active containers, and check deposition inputs.',' * @brief FFT2D5 deposition, line-density reduction, transverse solves and field gathering.\n *\n * Uses common-frame path projections, laboratory-normalized charge and the integrated\n * free-space transverse Green function. Diagnostic hooks expose the same numerical stages\n * to independent tests; no extra physical solver mode is selected here.');p.write_text(s)
