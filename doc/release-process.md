Release Process
====================

Before every release candidate:

* Update translations (ping wumpus on IRC) see [translation_process.md](translation_process.md).

* Update manpages, see [gen-manpages.sh](/contrib/devtools/README.md).

Before every minor and major release:

* Update [bips.md](bips.md) to account for changes since the last release.
* Update version in `configure.ac` (don't forget to set `CLIENT_VERSION_IS_RELEASE` to `true`)
* Write release notes (see below)
* Update `src/chainparams.cpp` nMinimumChainWork with information from the getblockchaininfo rpc.
* Update `src/chainparams.cpp` defaultAssumeValid  with information from the getblockhash rpc.
  - The selected value must not be orphaned so it may be useful to set the value two blocks back from the tip.
  - Testnet should be set some tens of thousands back from the tip due to reorgs there.
  - This update should be reviewed with a reindex-chainstate with assumevalid=0 to catch any defect
     that causes rejection of blocks in the past history.

Before every major release:

* Update hardcoded [seeds](/contrib/seeds/README.md).
* Update [`BLOCK_CHAIN_SIZE`](/src/qt/intro.cpp) to the current size plus some overhead.
* Update `src/chainparams.cpp` chainTxData with statistics about the transaction count and rate.
* Update version of `contrib/gitian-descriptors/*.yml`: usually one'd want to do this on master after branching off the release - but be sure to at least do it before a new major release

### First time / New builders

If you're using the automated script (found in [contrib/gitian-build.sh](/contrib/gitian-build.sh)), then at this point you should run it with the "--setup" command. Otherwise ignore this.

Check out the source code in the following directory hierarchy.

    cd /path/to/your/toplevel/build
    git clone https://github.com/LockTrip/Gitian-Sigs.git
    git clone https://github.com/LockTrip/Detached-Sigs.git
    git clone https://github.com/devrandom/gitian-builder.git
    git clone https://github.com/LockTrip/Blockchain.git

### HYDRA maintainers/release engineers, suggestion for writing release notes

Write release notes. git shortlog helps a lot, for example:

    git shortlog --no-merges v(current version, e.g. 0.7.2)..v(new version, e.g. 0.8.0)

Generate list of authors:

    git log --format='%aN' "$*" | sort -ui | sed -e 's/^/- /'

Tag version (or release candidate) in git

    git tag -s v(new version, e.g. 0.8.0)

### Setup and perform Gitian builds

If you're using the automated script (found in [contrib/gitian-build.sh](/contrib/gitian-build.sh)), then at this point you should run it with the "--build" command. Otherwise ignore this.

Setup Gitian descriptors:

    pushd ./HYDRA
    export SIGNER=(your Gitian key, ie bluematt, sipa, etc)
    export VERSION=(new version, e.g. 0.8.0)
    git fetch
    git checkout v${VERSION}
    popd

Ensure your Gitian-Sigs are up-to-date if you wish to gverify your builds against other Gitian signatures.

    pushd ./Gitian-Sigs
    git pull
    popd

Ensure gitian-builder is up-to-date:

    pushd ./gitian-builder
    git pull
    popd

### Fetch and create inputs: (first time, or when dependency versions change)

    pushd ./gitian-builder
    mkdir -p inputs
    wget -P inputs https://bitcoincore.org/cfields/osslsigncode-Backports-to-1.7.1.patch
    wget -P inputs http://downloads.sourceforge.net/project/osslsigncode/osslsigncode/osslsigncode-1.7.1.tar.gz
    popd

Create the OS X SDK tarball, see the [OS X readme](README_osx.md) for details, and copy it into the inputs directory.

### Optional: Seed the Gitian sources cache and offline git repositories

By default, Gitian will fetch source files as needed. To cache them ahead of time:

    pushd ./gitian-builder
    make -C ../HYDRA/depends download SOURCES_PATH=`pwd`/cache/common
    popd

Only missing files will be fetched, so this is safe to re-run for each build.

NOTE: Offline builds must use the --url flag to ensure Gitian fetches only from local URLs. For example:

    pushd ./gitian-builder
    ./bin/gbuild --url HYDRA=/path/to/hydra,signature=/path/to/sigs {rest of arguments}
    popd

The gbuild invocations below <b>DO NOT DO THIS</b> by default.

### Build and sign HYDRA for Linux, Windows, and OS X:

    pushd ./gitian-builder
    ./bin/gbuild --num-make 2 --memory 3000 --commit HYDRA=v${VERSION} ../HYDRA/contrib/gitian-descriptors/gitian-linux.yml
    ./bin/gsign --signer $SIGNER --release ${VERSION}-linux --destination ../Gitian-Sigs/ ../HYDRA/contrib/gitian-descriptors/gitian-linux.yml
    mv build/out/hydra-*.tar.gz build/out/src/hydra-*.tar.gz ../

    ./bin/gbuild --num-make 2 --memory 3000 --commit HYDRA=v${VERSION} ../HYDRA/contrib/gitian-descriptors/gitian-win.yml
    ./bin/gsign --signer $SIGNER --release ${VERSION}-win-unsigned --destination ../Gitian-Sigs/ ../HYDRA/contrib/gitian-descriptors/gitian-win.yml
    mv build/out/hydra-*-win-unsigned.tar.gz inputs/hydra-win-unsigned.tar.gz
    mv build/out/hydra-*.zip build/out/hydra-*.exe ../

    ./bin/gbuild --num-make 2 --memory 3000 --commit HYDRA=v${VERSION} ../HYDRA/contrib/gitian-descriptors/gitian-osx.yml
    ./bin/gsign --signer $SIGNER --release ${VERSION}-osx-unsigned --destination ../Gitian-Sigs/ ../HYDRA/contrib/gitian-descriptors/gitian-osx.yml
    mv build/out/hydra-*-osx-unsigned.tar.gz inputs/hydra-osx-unsigned.tar.gz
    mv build/out/hydra-*.tar.gz build/out/hydra-*.dmg ../
    popd

Build output expected:

  1. source tarball (`hydra-${VERSION}.tar.gz`)
  2. linux 32-bit and 64-bit dist tarballs (`hydra-${VERSION}-linux[32|64].tar.gz`)
  3. windows 32-bit and 64-bit unsigned installers and dist zips (`hydra-${VERSION}-win[32|64]-setup-unsigned.exe`, `hydra-${VERSION}-win[32|64].zip`)
  4. OS X unsigned installer and dist tarball (`hydra-${VERSION}-osx-unsigned.dmg`, `hydra-${VERSION}-osx64.tar.gz`)
  5. Gitian signatures (in `Gitian-Sigs/${VERSION}-<linux|{win,osx}-unsigned>/(your Gitian key)/`)

### Verify other gitian builders signatures to your own. (Optional)

Add other gitian builders keys to your gpg keyring, and/or refresh keys.

    gpg --import HYDRA/contrib/gitian-keys/*.pgp
    gpg --refresh-keys

Verify the signatures

    pushd ./gitian-builder
    ./bin/gverify -v -d ../Gitian-Sigs/ -r ${VERSION}-linux ../HYDRA/contrib/gitian-descriptors/gitian-linux.yml
    ./bin/gverify -v -d ../Gitian-Sigs/ -r ${VERSION}-win-unsigned ../HYDRA/contrib/gitian-descriptors/gitian-win.yml
    ./bin/gverify -v -d ../Gitian-Sigs/ -r ${VERSION}-osx-unsigned ../HYDRA/contrib/gitian-descriptors/gitian-osx.yml
    popd

### Next steps:

Commit your signature to Gitian-Sigs:

    pushd Gitian-Sigs
    git add ${VERSION}-linux/${SIGNER}
    git add ${VERSION}-win-unsigned/${SIGNER}
    git add ${VERSION}-osx-unsigned/${SIGNER}
    git commit -a
    git push  # Assuming you can push to the Gitian-Sigs tree
    popd

Codesigner only: Create Windows/OS X detached signatures:
- Only one person handles codesigning. Everyone else should skip to the next step.
- Only once the Windows/OS X builds each have 3 matching signatures may they be signed with their respective release keys.

Codesigner only: Sign the osx binary:

    transfer hydra-osx-unsigned.tar.gz to osx for signing
    tar xf hydra-osx-unsigned.tar.gz
    ./detached-sig-create.sh -s "Key ID"
    Enter the keychain password and authorize the signature
    Move signature-osx.tar.gz back to the gitian host

Codesigner only: Sign the windows binaries:

    tar xf hydra-win-unsigned.tar.gz
    ./detached-sig-create.sh -key /path/to/codesign.key
    Enter the passphrase for the key when prompted
    signature-win.tar.gz will be created

Codesigner only: Commit the detached codesign payloads:

    cd ~/Detached-Sigs
    checkout the appropriate branch for this release series
    rm -rf *
    tar xf signature-osx.tar.gz
    tar xf signature-win.tar.gz
    git add -a
    git commit -m "point to ${VERSION}"
    git tag -s v${VERSION} HEAD
    git push the current branch and new tag

Non-codesigners: wait for Windows/OS X detached signatures:

- Once the Windows/OS X builds each have 3 matching signatures, they will be signed with their respective release keys.
- Detached signatures will then be committed to the [HYDRA Detached Sigs](https://github.com/LockTrip/Detached-Sigs) repository, which can be combined with the unsigned apps to create signed binaries.

Create (and optionally verify) the signed OS X binary:

    pushd ./gitian-builder
    ./bin/gbuild -i --commit signature=v${VERSION} ../HYDRA/contrib/gitian-descriptors/gitian-osx-signer.yml
    ./bin/gsign --signer $SIGNER --release ${VERSION}-osx-signed --destination ../Gitian-Sigs/ ../HYDRA/contrib/gitian-descriptors/gitian-osx-signer.yml
    ./bin/gverify -v -d ../Gitian-Sigs/ -r ${VERSION}-osx-signed ../HYDRA/contrib/gitian-descriptors/gitian-osx-signer.yml
    mv build/out/hydra-osx-signed.dmg ../hydra-${VERSION}-osx.dmg
    popd

Create (and optionally verify) the signed Windows binaries:

    pushd ./gitian-builder
    ./bin/gbuild -i --commit signature=v${VERSION} ../HYDRA/contrib/gitian-descriptors/gitian-win-signer.yml
    ./bin/gsign --signer $SIGNER --release ${VERSION}-win-signed --destination ../Gitian-Sigs/ ../HYDRA/contrib/gitian-descriptors/gitian-win-signer.yml
    ./bin/gverify -v -d ../Gitian-Sigs/ -r ${VERSION}-win-signed ../HYDRA/contrib/gitian-descriptors/gitian-win-signer.yml
    mv build/out/hydra-*win64-setup.exe ../hydra-${VERSION}-win64-setup.exe
    mv build/out/hydra-*win32-setup.exe ../hydra-${VERSION}-win32-setup.exe
    popd

Commit your signature for the signed OS X/Windows binaries:

    pushd Gitian-Sigs
    git add ${VERSION}-osx-signed/${SIGNER}
    git add ${VERSION}-win-signed/${SIGNER}
    git commit -a
    git push  # Assuming you can push to the Gitian-Sigs tree
    popd

### After 3 or more people have gitian-built and their results match:

- Create `SHA256SUMS.asc` for the builds, and GPG-sign it:

```bash
sha256sum * > SHA256SUMS
```

The list of files should be:
```
hydra-${VERSION}-aarch64-linux-gnu.tar.gz
hydra-${VERSION}-arm-linux-gnueabihf.tar.gz
hydra-${VERSION}-i686-pc-linux-gnu.tar.gz
hydra-${VERSION}-x86_64-linux-gnu.tar.gz
hydra-${VERSION}-osx64.tar.gz
hydra-${VERSION}-osx.dmg
hydra-${VERSION}.tar.gz
hydra-${VERSION}-win32-setup.exe
hydra-${VERSION}-win32.zip
hydra-${VERSION}-win64-setup.exe
hydra-${VERSION}-win64.zip
```
The `*-debug*` files generated by the gitian build contain debug symbols
for troubleshooting by developers. It is assumed that anyone that is interested
in debugging can run gitian to generate the files for themselves. To avoid
end-user confusion about which file to pick, as well as save storage
space.

- GPG-sign it, delete the unsigned file:
```
gpg --digest-algo sha256 --clearsign SHA256SUMS # outputs SHA256SUMS.asc
rm SHA256SUMS
```
(the digest algorithm is forced to sha256 to avoid confusion of the `Hash:` header that GPG adds with the SHA256 used for the files)
Note: check that SHA256SUMS itself doesn't end up in SHA256SUMS, which is a spurious/nonsensical entry.

- To upload binaries to gitlab tag - execute the following command from the directory of the binaries
```bash
for filename in *.*; do curl --request POST --header "PRIVATE-TOKEN: <PRIVATE_TOKEN>" --form "file=@${filename}" https://gitlab.com/api/v4/projects/<PROJECT_ID>/uploads | json_pp; done
```
- To get the project id - execute the following command 
```bash
curl -XGET --header "PRIVATE-TOKEN: <PRIVATE_TOKEN>" "https://gitlab.com/api/v4/projects/LockTrip-Dev-Team%2FLockTrip" | json_pp
```

- Announce the release:

  - Archive release notes for the new version to `doc/release-notes/` (branch `master` and branch of the release)

  - Create a [new GitHub release](https://github.com/LockTrip/Blockchain/releases/new) with a link to the archived release notes.

  - Celebrate
