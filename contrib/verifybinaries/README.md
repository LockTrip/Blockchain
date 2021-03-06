### Verify Binaries

#### Preparation:

Make sure you obtain the proper release signing key and verify the fingerprint with several independent sources.

```sh
$ gpg --fingerprint "HYDRA binary release signing key"
pub   4096R/36C2E964 2015-06-24 [expires: 2017-02-13]
      Key fingerprint = 01EA 5486 DE18 A882 D4C2  6845 90C8 019E 36C2 E964
uid                  Wladimir J. van der Laan (HYDRA binary release signing key) <laanwj@gmail.com>
```

#### Usage:

This script attempts to download the signature file `SHA256SUMS.asc` from https://github.com/LockTrip/Blockchain/releases

It first checks if the signature passes, and then downloads the files specified in the file, and checks if the hashes of these files match those that are specified in the signature file.

The script returns 0 if everything passes the checks. It returns 1 if either the signature check or the hash check doesn't pass. If an error occurs the return value is 2.


```sh
./verify.sh hydra-0.1
```

If you only want to download the binaries of certain platform, add the corresponding suffix, e.g.:

```sh
./verify.sh hydra-0.1-osx
./verify.sh hydra-0.1-linux
./verify.sh hydra-0.1-rc3-win64
```

If you do not want to keep the downloaded binaries, specify anything as the second parameter.

```sh
./verify.sh hydra-0.1 delete
```
