# Opensmt's Proof-checker

The proof checker checks
[opensmt](https://github.com/usi-verification-and-security/opensmt)'s
trails.  Note: contact antti.hyvarinen@gmail.com to get the proof
producing version of opensmt.

## installation

```
mkdir build
cd build
cmake ..
make -j
make install
```

## Usage

```
proof-check.sh -t <trail>
```

## Details

The proof checker is now compatible with
[smt-comp](https://smt-comp.github.io/2022/)'s proof track.  In the
current version the compatibility is a little artificial.  It's simply a
base64-encoded version of a .tar.bz2 file of the "real" proof.  The
"real" proof on the other hand is constructed in a sub-folder of the
working directory called proof as the solver runs.  The proof checker's
main binary is `proof-check.sh`, it reads the encoded file, decompresses
it, and runs the modular proof / trail checkers.

For more details on the technology, please check our
[DAC 2021 paper](https://ieeexplore.ieee.org/document/9586272):
*Rodrigo Otoni, Martin Blicha, Patrick Eugster, Antti E. J. Hyvärinen,
Natasha Sharygina: Theory-Specific Proof Steps Witnessing Correctness of
SMT Executions.  DAC 2021: 541-546*



