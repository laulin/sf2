# SF2

This piece of software is used to encrypt, decrypt and edit text file.

**Disclaimer** : You use SF2 as is, with no guarantee of results. I cannot be responsible for any loss, alteration or disclosure of data.

## Why use SF2 ?

* Encrypt or decrypt text file like your personal diary
* Transfert over wire one small file
* Edit a note text file you want to keep private

## Why **not** use SF2 ?

* Encrypt large file like video
* Protect yourself against NSA, DGSI, CIA, etc
* Protect financial/military/compromat
* **In no case where a guarantee would be necessary**

## Understand the behavious

The encryption use the Fernet algorithm ([specification](https://github.com/fernet/spec/blob/master/Spec.md)), which use following strong algorithm :

* AES 128 with CBC mode (encryption)
* HMAC-SHA256 (authentication/integrity)
* IV is created with robust random function (os.getrandom)

It uses a password (symetric algorithm with preshared key). The key derivation function - the way the password is processed to get a key - is the PBKDF2HMAC algorithm with 16 bytes random salt and 480000 iterations.

Currently (19/08/2022), these algorithms are considered safe.

**Any security problem ? gignops+security->gmail.com**

## How to use it

Now that the boring stuff is said, let's move on to the interesting part.

### Install

At first you need to install SF2. You have two options :

* From the repo :
  * git clone https://github.com/laulin/sf2.git
  * python3 -m build
  * pip3 install build/sf2-*-py3-none-any.whl
* [Recommanded] pip3 install sf2

### Encrypt

To encrypt a file, run this command : 

`sf2 -e -i your_plaintext_file.txt -o your_encrypted_file.x`

Enter the password twice and it will create the encrypted version (your_encrypted_file.x) or your source file (your_plaintext_file.txt).

### Decrypt

To decrypt a file, run this command :

`sf2 -f -i your_encrypted_file.x -o your_decrypted_file.txt `

### Verify

To check a password on a file, run this command :

`sf2 --verify -i your_encrypted_file.x `

After entering the password, it will display "OK" or "FAILED !". I think it's pretty clear

### Edit with external GUI

LYou can edit your file, but with external editor (nano, vim, mousepad, etc). Default is *mousepad* : 

`sf2 --edit -i your_encrypted_file.x `

To select another editor (let's say nano) :

`sf2 --edit -i your_encrypted_file.x --editor nano`

### Create a new encrypted file

To create a new empty and encrypt file, run this command :

`sf2 --n -i your_empty_encrypted_file.x`

## Practical considerations

If you expect to protect a file from a data disclosure in case of hardware theft, **never** store you sensitive file on the hardware. If you need to use another editor than the one included in SF2, you must extract your file to a RAM partition (TMPFS, RAMFS). Prefered using --external option in this case, more easy. 

## Supported system

I currently only work on linux (Debian based distributions). I don't known how it works on other OS.

## Acknowledgement

Thanks to [Spartan Conseil](https://spartan-conseil.fr) for the support !