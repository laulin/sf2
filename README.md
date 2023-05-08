# SF2

This software allows you to secure your files and work on them as a team in the cloud. And it's very simple: all you need is an SSH key!

## Why use SF2 ?

* Just secure a file with a password
* Share a file with a team in a shared FS
* Allow machines to acces to an encrypted file without using password

## Install

At first you need to install SF2. You have two options :

* [Recommanded] pip3 install sf2
* From the [github releases](https://github.com/laulin/sf2/releases/), download the binary file, copy it to /usr/local/bin and make it executable of all. Currently only for X86/debian based.
* From the repo :
  * git clone https://github.com/laulin/sf2.git
  * python3 -m build
  * pip3 install build/sf2-*-py3-none-any.whl

## Quickstart

### Create a container

``` bash
sf2 new my_container.x
```

If you need multiple encrypted container with the same password, you can add as many files as you want :

``` bash
sf2 new my_container.x foobar.x stuff.x ...
```

### Add SSH key

By default, the current user ssh public key is used :

``` bash
sf2 ssh add my_container.x
```

If you need to add another key (e.g. that of a colleague), you must have the file and provide it as a parameter:

``` bash
sf2 ssh add -k path/to/id_rsa.pub my_container.x
```

The auth id, i.e. the unique identifier of the user in relation to his key, is by default with this command the one present with the ssh key (example foo@bar). But it can be interesting to redefine it according to your needs: 

``` bash
sf2 ssh add -k path/to/id_rsa.pub -a ironman my_container.x
```

### Open a container

Once the ssh key is added, it is easy to access the data through a program : 

``` bash
sf2 ssh open -p nano my_container.x
```
The program used must be blocking. Indeed, it is that the command ends, the information written in ram is carried over in the container and deleted.

A templating system is available and allows the execution of a treatment on the data, as if the file was available in clear on the machine:

``` bash
sf2 open -p "echo -n 'foobar' >> {filename}; cat {filename}"  my_container.x
```

Only one container can be opened at a time.

### List SSH keys

Display by container the list of auth id and associated keys:

``` bash
sf2 ssh add my_container.x
```

### Remove a key

It is possible to remove a public key from the auth id : 

``` bash
sf2 ssh rm -a foo@bar my_container.x
```

### Encrypt

Sometimes it is necessary to create a container from an existing file and not *ex nihilo* as the new command does: 

``` bash
sf2 encrypt -i data.txt -o my_container.x
```

### Decrypt

**WARNING** : this action is dangerous and can lead to data leak.

To extract the information secured in a container to a plain text file, you must do the following:

``` bash
sf2 decrypt -i my_container.x -o plain.txt
```

### Desktop application

A graphic version of SF2 is available. It allows to perform all the operations of the CLI version but with a nice interface :

``` bash
sf2 app
```

It contains small manual and contextual help.

## Advanced

### Password vs SSH key

Only the 'new', 'encrypt', and 'ssh add' functions require the password. All other functions use SSH keys by default. It is possible to bypass this behavior by adding the '--password' directive to the command. For example, here the "open" function with password :

``` bash
sf2 open --password -p cat my_container.x
```

In the context of using the password, the -m option allows you to set the password on the command line (Warning: this can be dangerous). 

By default, only passwords of 12 characters (A-Z, a-z, 0-9, special symbols) are allowed. Functions 'new', 'encrypt', and 'ssh add' will raise an exception if the password is not compliant. Anyway, you can bypass this procetion using "-w" option.

``` bash
# /!\ This is a very bad idea, for testing purpose only
sf2 new -m foobar -w my_container.x
```

### Auth ID and SSH key

As seen in the quickstart, by default the public key add function uses the user's public SSH key (RSA only). It is possible to specify a key (-k), and in this case, the auth id will be that of the key. In both of the previous cases, you can manually change the auth id (-a).

For usage involving decryption with the private key, it is necessary to obtain both the private key and the auth id. For both, the following priority order applies: command parameter, config file (see below), and default value. For the auth_id, the default value is user@machine, and for the private key, /home/user/.ssh/id_rsa is used. If the private key is not found (or is incorrect), an error is raised.

The arguments to define the private key file, the auth id, and the private key password (if it is encrypted) are respectively '-y', '-a', and '-K'.

### Configfile

Similar to SSH and its .ssh directory in the home folder, it is possible to define a config file for sf2: /home/user/.sf2/config.yaml. Each entry is defined by the path of the concerned file and can set the private key (private_key_file), the auth id (auth_id), and the program used to open it (program). Here is an example:

```yaml
/tmp/encrypted.x:
  private_key_file : /keys/id_rsa
  auth_id: test@test
  # {filename} or [filename] are valid
  program: nano [filename]
```
The "program" parameter is very useful for a straight forward "open" function.

### Container format

By default, container uses mesage pack format. In particular cas, a non binary file can be need. The "--format json" parameter allows do this.

### Legacy format

Currently, SF2 is in version 2.x. The previous version (e.g 1.x) is not directly supported, but it can be converted to 2.x. 

``` bash
sf2 convert -i version1.x -o version2.x
```

## Understand the behavious

Under the hood, symmetric encryption (and more) is achieved by the Fernet algorithm ([specification](https://github.com/fernet/spec/blob/master/Spec.md)), which use following strong algorithms :

* AES 128 with CBC mode (encryption)
* HMAC-SHA256 (authentication/integrity)
* IV is created with robust random function (secrets)

The data is encrypted with a first key (master data key) of 32 bits. This key is itself encrypted with a second key (master key) of 32 bits, resulting from the derivation of the password. This derivation uses a key derivation function (KDF, SHA256) with 32 bits of IV and 48000 iterations.

This double stage approach allows the second part, which is the use of asymmetric RSA keys in SSH format. With the password, we obtain the "master key". The latter can then be encrypted with the public key and only decrypted with the private key. As many public keys as necessary can be added to the encrypted container.

Access to a shared file is a complex task. It is necessary to lock the file in writing to avoid conflicts between users. We have used the flufl.lock library which solves this problem. It works locally but also via NFS.

It is possible to open the file through a command (see open). This opening is done via a temporary file in RAM: no unencrypted data is ever written to the disk.

## Security recommandations

The first recommendation is to use a strong password. Basically, SF2 forces you to be serious about this point but this may not be enough. Always keep in mind that the security of a symmetric system relies mainly on the security of the secret.

That's why it is recommended to use only SSH keys. Indeed, setting up a strong and unique password for each file can be very hard to type. On the other hand, the use of your SSH key is simple and can even be transparent.

As said above, security is based on the password. It is not recommended to use the "-m" option to put the password in the command, which would allow it to be leaked via history or by listing processes.

Finally you should only add SSH keys from trusted machines/persons. Indeed with his private key, a malicious person can recover the master key and add other keys. So be careful.

The use of the "decrypt" function should only be done for a particular use and in a secure environment. To read or write data protected by the container, you must use the "open" function. It prevents any unencrypted data from being written to the hard disk. By not respecting this, you expose yourself to a data leakage (compromised machine, disk forensic, etc).

**Any security problem ? gignops+security->gmail.com**

## Supported system

I currently only work on linux (Debian based distributions). I don't known how it works on other OS.

## Acknowledgement

Thanks to [Spartan Conseil](https://spartan-conseil.fr) for the sponsoring !