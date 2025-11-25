背景
--

        笔者住的地方大门是智能门禁锁，需要刷身份证或指纹进出，但指纹识别不灵敏经常验证失败，使用身份证可以打开，但是身份证携带不便，更糟糕的是如果丢失了是比较麻烦的。笔者经过仔细观察和对比实验，推测智能门禁锁没有读取身份证里的个人信息，应该只是读取了某种id标识。笔者在此之前有简单复制过小区门禁卡的经验，知道每个ic卡都有唯一的id号，二代证也是一种ic卡，应当也有一个未加密的id号，所以推测智能门禁锁只读取了二代身份证的某种id标识。之所以这么推测是因为一方面是因为二代证里面的个人这些信息是加密的，除非经过授权，否则是无法直接读取的，另一方面实验发现即使是同一个人的新旧身份证也只有登记录入过的身份证才能打开，这让笔者更加坚定智能门禁锁是读取二代证id的。因此产生了将二代身份证的id复制到门禁卡中，用门禁卡来代替身份证刷卡的想法。

         产生了这种想法后，笔者通过互联网检索资料了解到二代证确实是一种IC卡，是遵循ISO14443 Type B协议的卡片，不过二代证里面的id标识搞单片机的网友称它为uid，未加密可直接读取，长度为8字节。ISO14443标准的IC卡与手机nfc的频率相同，都是13.56mhz，可以使用PN532或者ACR122U等设备进行读写。PN532比ACR122U便宜很多，淘宝拼多多通常30元就可以买到。遂在网上下单购买了一个PCR532来进行尝试，店家号称是PN532的升级版，实际测试发现底层驱动和配置文件里面写的都是PN532，“二代升级的PCR532”这种说法感觉像是忽悠像我这种不懂行的小白。

        这里需要说明的是，笔者运气较好，在不懂行随意买的情况下买到的是那种带usb type-c接口的长方形的PCR532板子，颜色是黑色的。后来在网上检索资料时，有人说有的PN532(红色方形的那款)读不到卡片，看其他人的回复说可能是这种板子设计或者质量不好，所以尽量不要买红色板子那款。

我买的长这样（下图）

![](https://img2023.cnblogs.com/blog/733392/202307/733392-20230718095444003-2059489391.png)

据说读不到卡片的长这样(下图)

![](https://img2023.cnblogs.com/blog/733392/202307/733392-20230718095537837-210365501.png)

运行环境
----

 本文先在arm的树莓派上进行了编译、配置、读取，随后为确保不受环境影响，在全新的Ubuntu 22 desktop上进行了验证。

树莓派环境：

[![复制代码](//assets.cnblogs.com/images/copycode.gif)](javascript:void(0); "复制代码")

Linux raspberrypi 6.1.21-v8+ #1642 SMP PREEMPT Mon Apr  3 17:24:16 BST 2023 aarch64 GNU/Linux

PRETTY\_NAME="Debian GNU/Linux 11 (bullseye)"
NAME="Debian GNU/Linux"
VERSION\_ID="11"
VERSION="11 (bullseye)"
VERSION\_CODENAME=bullseye
ID=debian
HOME\_URL="https://www.debian.org/"
SUPPORT\_URL="https://www.debian.org/support"
BUG\_REPORT\_URL="https://bugs.debian.org/"

gcc version 10.2.1 20210110 (Debian 10.2.1-6)

[![复制代码](//assets.cnblogs.com/images/copycode.gif)](javascript:void(0); "复制代码")

ubuntu 22 desktop 环境

[![复制代码](//assets.cnblogs.com/images/copycode.gif)](javascript:void(0); "复制代码")

Linux lenovo 5.19.0-32-generic #33~22.04.1-Ubuntu SMP PREEMPT\_DYNAMIC Mon Jan 30 17:03:34 UTC 2 x86\_64 x86\_64 x86\_64 GNU/Linux

PRETTY\_NAME="Ubuntu 22.04.2 LTS"
NAME="Ubuntu"
VERSION\_ID="22.04"
VERSION="22.04.2 LTS (Jammy Jellyfish)"
VERSION\_CODENAME=jammy
ID=ubuntu
ID\_LIKE=debian
HOME\_URL="https://www.ubuntu.com/"
SUPPORT\_URL="https://help.ubuntu.com/"
BUG\_REPORT\_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY\_POLICY\_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
UBUNTU\_CODENAME=jammy

gcc version 11.3.0 (Ubuntu 11.3.0-1ubuntu1~22.04.1) 

[![复制代码](//assets.cnblogs.com/images/copycode.gif)](javascript:void(0); "复制代码")

读取流程
----

由于对单片机这种硬件不太了解，在网络上找了很多资料，花了好几个小时才摸索明白，因此本文的个别描述可能存在错误，如读者发现问题，请不吝指出。

看网上说因为二代证 ATRB返回值非标，所以需要自己定制读取逻辑，这就需要驱动来操纵PN532设备，驱动网上有开源的libnfc，地址在这里 **[GitHub - nfc-tools/libnfc](https://github.com/nfc-tools/libnfc)**，因为不知道这个库支不支持Windows版本，所以我在Linux(arm的树莓派)下进行的编译。

以下是具体步骤

### 1\. 下载libnfc-1.8.0库

已上传到博客，地址：**[libnfc-1.8.0](https://files.cnblogs.com/files/pluse/libnfc-1.8.0.zip?t=1689646032&download=true)** ，下载后解压即可

### 2\. 设置寄存器配置

这里为什么要设置寄存器？下面是网上找到的说法：

> 由于二代证的ATTRIB操作非标，所以不能直接用PN532提供的InListPassiveTarget等上层指令来选卡，  
> 只能靠自己设置寄存器，并通过InCommunicateThru底层通讯，发送ATQB和ATTRIB，完成选卡操作。

这里面说要设置寄存器的值，所以在 libnfc/chips/pn53x.c 文件中 int pn53x\_reset\_settings(struct nfc\_device \*pnd)函数中添加了12行寄存器设置代码。但是这个 InCommunicateThru 是啥东西，确实没搞明白。另外一个大佬提到的PCD发送命令，这个PCD是啥也没搞懂，最后没用到这些也成功了(也可能是调用栈函数里面用到了，只有我不懂而已，2333)

如下图，添加了156-169行，libnfc-1.8.0库libnfc/chips/pn53x.c文件中的行数与下图不一样，行数与截图不同可以忽略，这是因为笔者本地编辑器对源码做了格式化。添加的代码文本在截图后

![](https://img2023.cnblogs.com/blog/733392/202307/733392-20230718102808140-688077467.png) 

添加的寄存器配置：

[![复制代码](//assets.cnblogs.com/images/copycode.gif)](javascript:void(0); "复制代码")

    pn53x\_write\_register(pnd, PN53X\_REG\_CIU\_Mode, 0xff, 0xff);
    pn53x\_write\_register(pnd, PN53X\_REG\_CIU\_TxAuto, 0xff, 0x00);
    pn53x\_write\_register(pnd, PN53X\_REG\_CIU\_TxMode, 0xff, 0x03);
    pn53x\_write\_register(pnd, PN53X\_REG\_CIU\_RxMode, 0xff, 0x03);
    pn53x\_write\_register(pnd, PN53X\_REG\_CIU\_TypeB, 0xff, 0x03);
    pn53x\_write\_register(pnd, PN53X\_REG\_CIU\_Demod, 0xff, 0x4d);
    pn53x\_write\_register(pnd, PN53X\_REG\_CIU\_GsNOn, 0xff, 0xff);
    pn53x\_write\_register(pnd, PN53X\_REG\_CIU\_CWGsP, 0xff, 0x3f);
    pn53x\_write\_register(pnd, PN53X\_REG\_CIU\_ModGsP, 0xff, 0x18);
    pn53x\_write\_register(pnd, PN53X\_REG\_CIU\_RxThreshold, 0xff, 0x4d);
    pn53x\_write\_register(pnd, PN53X\_REG\_CIU\_ModWidth, 0xff, 0x68);
    pn53x\_write\_register(pnd, PN53X\_REG\_CIU\_ManualRCV, 0xff, 0x10);

    printf("\\npn53x\_write\_register set register \*\*\*\*\*\*\\n");

[![复制代码](//assets.cnblogs.com/images/copycode.gif)](javascript:void(0); "复制代码")

### 3\. 定制读取二代证uid逻辑

已上传到博客，地址 **[二代证uid读取程序](https://files.cnblogs.com/files/pluse/nfc-anticol.c.zip?t=1689732821&download=true)** ，为防止失效，文章底部贴了源码文本

这一步是定制读取二代身份证uid的指令逻辑，也就是发送REQB、ATTRIB指令的逻辑。在官方libnfc-1.8.0/example目录下的nfc-anticol.c示例代码中直接对其加以修改获得可读二代证uid的程序。修改后暂时无需编译，因为这一步是在官方库example中原地修改的，后续make时会自动编译该目录下的代码。

### 4\. 编译libnfc

PS:  编译环境如文章开头所说明，需要事先准备好gcc编译环境，如果没有，可以使用下面的命令进行安装

sudo apt-get install build-essentail -y

这里编译时指定了 nfc相关的配置文件目录为 /etc，--with-drivers 选项指定了驱动为pn532\_uart，没有使用pn53x\_usb，明明是Usb type-c口连接的PN532设备，但是要使用pn532\_uart串口驱动是为啥，笔者也没搞懂，笔者实测发现，即使编译了pn53x\_usb的驱动，在查找nfc设备时，pn53x\_usb的驱动也会提示没找到，只有pn532\_uart能找到设备

cd libnfc-1.8.0/
./configure --sysconfdir=/etc --with-drivers='pn532\_uart'
make clean
make

### 5. 连接nfc设备

在代码编译准备妥当之后，需要用usb type-c线连接设备和电脑。如果没有多个其他设备存在，连接PN532后，会看到/dev/ttyUSB0这个设备文件，如果在Ubuntu 22.04的系统找不到/dev/ttyUSB0，可能是因为一个软件冲突了，可以将其卸载后再重新插拔连接一下设备

sudo apt-get remove brltty

如果不是Ubuntu 22或者卸载了上面的软件重新插拔设备后依然找不到/dev/ttyUSB0，可能是连接pn532设备用的type-c线有问题，有些廉价线或者赠送的type-c线可能导致识别不到，因为那些线为了成本少了一些针脚，只能充电或基本传输，可以仔细看下图，2根type-c线内部金属节点有区别。

![](https://img2023.cnblogs.com/blog/733392/202307/733392-20230718222647741-620438584.png)

在能够看到/dev/ttyUSB0设备文件之后，如果是以普通用户进行设备的读写，那么还需要给设备添加读写权限

sudo chmod 777 /dev/ttyUSB0

当然，以上步骤都假定PN532连接电脑后，在Linux中被命名为/dev/ttyUSB0，具体是不是这个名字，可以使用 ls 命令查看 /dev 目录下以 ttyUSB开头的文件来进行确认。

### 6\. 配置libnfc配置文件

当设备连接妥当之后，就可以准备用 nfc-list 命令进行读取测试了(nfc-list命令是第4步中make编译出来的，在 libnfc-1.8.0/utils 目录下)，这个命令以及其他nfc相关命令在能使用之前，需要先配置这些命令用到的一个配置文件，因为在第4步中编译指定的配置文件目录前缀为/etc，所以这个配置文件是 /etc/nfc/libnfc.conf，这个文件是用于nfc相关命令使用的配置，其中name是给目标设备的命名，connstring是连接串，猜测 pn532\_uart 是通信方式，/dev/ttyUSB0 是通信设备，也就是PN532(PCR532)，两个allow是扫描配置。其中/dev/ttyUSB0这个文件名需要根据第5步中的实际情况来写。

此处需要使用root用户权限来执行

[![复制代码](//assets.cnblogs.com/images/copycode.gif)](javascript:void(0); "复制代码")

mkdir /etc/nfc
cat > /etc/nfc/libnfc.conf <<EOF

device.name = "PN532-NFC-DEVICE"
device.connstring = "pn532\_uart:/dev/ttyUSB0"
allow\_intrusive\_scan = true
allow\_autoscan = true

EOF

[![复制代码](//assets.cnblogs.com/images/copycode.gif)](javascript:void(0); "复制代码")

### 7\. 读取二代证uid

 在编译完libnfc库，连接上设备，配置好config文件之后，就可以尝试读取了，这里使用第3步中make编译出来的修改后的nfc-anticol程序来进行读取，结果如下

[![复制代码](//assets.cnblogs.com/images/copycode.gif)](javascript:void(0); "复制代码")

\# cd libnfc-1.8.0/examples
# ./nfc-anticol
NFC reader: pn532\_uart:/dev/ttyUSB0 opened

Sent bits: 05 00 00 71 ff
Received bits: 50 00 00 00 00 d1 03 00 81 00 70 90 84 10
PUPI: 00 00 00 00
Sent bits: 1d 00 00 00 00 00 08 01 08 f3 10
Received bits: @@ @@ @@
Sent bits: 00 36 00 00 08 57 44
Received bits: ## ## ## ## ## ## ## ## $$ $$ $$ $$

[![复制代码](//assets.cnblogs.com/images/copycode.gif)](javascript:void(0); "复制代码")

上面./nfc-anticol程序执行的输出中最后一行前16位(8个字节)就是二代身份证的uid了，最后8位(4个字节)似乎是校验码

插曲
--

笔者购买的PCR532设备有附赠的操作软件，该软件是Windows平台的，刚买到设备后，笔者没有仔细去把玩Windows平台的这个配套的软件就简单认为该软件不支持二代身份证uid的读取，就在笔者花了大半个下午的时间摸索出来linux平台定制读取uid逻辑并成功读取之后，随手翻了翻赠送软件的功能菜单，竟然意外发现在软件某个不起眼的界面中有着“读取身份证uid”的功能按钮....

笔者测试了附赠软件提供的这个功能，发现与文章前面一番功夫读取出来的uid是相同的，这倒是间接验证了前面的折腾是正确的 :P

![](https://img2023.cnblogs.com/blog/733392/202307/733392-20230721221540048-821892396.png)

结果
--

走到这里，二代身份证的UID已经读取到了，但不幸的是，这个UID长度是8个字节，没法写入普通门禁卡中，因为普通门禁卡的id是4个字节+1个字节校验码，显然二代身份证的UID是没法写入到普通门禁卡中的，最终以失败告终....

 定制读取uid源码
----------

[![复制代码](//assets.cnblogs.com/images/copycode.gif)](javascript:void(0); "复制代码")

#ifdef HAVE\_CONFIG\_H
#include "config.h"
#endif // HAVE\_CONFIG\_H

#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#include <nfc/nfc.h>

#include "utils/nfc-utils.h"

#define SAK\_FLAG\_ATS\_SUPPORTED 0x20

#define MAX\_FRAME\_LEN 264

static uint8\_t abtRx\[MAX\_FRAME\_LEN\];
static size\_t szRx = sizeof(abtRx);
static nfc\_device \*pnd;

bool quiet\_output = false;
bool force\_rats = false;
bool timed = false;
bool iso\_ats\_supported = false;

// ISO14443A Anti-Collision Commands
uint8\_t abtReqa\[1\] = {0x26};
uint8\_t abtSelectAll\[2\] = {0x93, 0x20};
uint8\_t abtSelectTag\[9\] = {0x93, 0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
uint8\_t abtRats\[4\] = {0xe0, 0x50, 0x00, 0x00};
uint8\_t abtHalt\[4\] = {0x50, 0x00, 0x00, 0x00};
#define CASCADE\_BIT 0x04

static bool
transmit\_bytes(const uint8\_t \*pbtTx, const size\_t szTx)
{
    uint32\_t cycles \= 0;
    // Show transmitted command
    if (!quiet\_output)
    {
        printf("Sent bits:     ");
        print\_hex(pbtTx, szTx);
    }
    int res;
    // Transmit the command bytes
    if (timed)
    {
        if ((res = nfc\_initiator\_transceive\_bytes\_timed(pnd, pbtTx, szTx, abtRx, sizeof(abtRx), &cycles)) < 0)
            return false;
        if ((!quiet\_output) && (res > 0))
        {
            printf("Response after %u cycles\\n", cycles);
        }
    }
    else
    {
        if ((res = nfc\_initiator\_transceive\_bytes(pnd, pbtTx, szTx, abtRx, sizeof(abtRx), 0)) < 0)
            return false;
    }
    szRx \= res;
    // Show received answer
    if (!quiet\_output)
    {
        printf("Received bits: ");
        print\_hex(abtRx, szRx);
    }
    // Succesful transfer
    return true;
}

int main()
{
    nfc\_context \*context;
    nfc\_init(&context);
    if (context == NULL)
    {
        ERR("Unable to init libnfc (malloc)");
        exit(EXIT\_FAILURE);
    }

    // Try to open the NFC reader
    pnd = nfc\_open(context, NULL);

    if (pnd == NULL)
    {
        ERR("Error opening NFC reader");
        nfc\_exit(context);
        exit(EXIT\_FAILURE);
    }

    // Initialise NFC device as "initiator"
    if (nfc\_initiator\_init(pnd) < 0)
    {
        nfc\_perror(pnd, "nfc\_initiator\_init");
        nfc\_close(pnd);
        nfc\_exit(context);
        exit(EXIT\_FAILURE);
    }

    // Configure the CRC
    if (nfc\_device\_set\_property\_bool(pnd, NP\_HANDLE\_CRC, false) < 0)
    {
        nfc\_perror(pnd, "nfc\_device\_set\_property\_bool");
        nfc\_close(pnd);
        nfc\_exit(context);
        exit(EXIT\_FAILURE);
    }
    // Use raw send/receive methods
    if (nfc\_device\_set\_property\_bool(pnd, NP\_EASY\_FRAMING, false) < 0)
    {
        nfc\_perror(pnd, "nfc\_device\_set\_property\_bool");
        nfc\_close(pnd);
        nfc\_exit(context);
        exit(EXIT\_FAILURE);
    }
    // Disable 14443-4 autoswitching
    if (nfc\_device\_set\_property\_bool(pnd, NP\_AUTO\_ISO14443\_4, false) < 0)
    {
        nfc\_perror(pnd, "nfc\_device\_set\_property\_bool");
        nfc\_close(pnd);
        nfc\_exit(context);
        exit(EXIT\_FAILURE);
    }

    printf("NFC reader: %s opened\\n\\n", nfc\_device\_get\_name(pnd));

    uint8\_t PUPI\[4\];

    uint8\_t REQB\[5\] = {0x05, 0x00, 0x00};
    iso14443b\_crc\_append(REQB, 3);
    transmit\_bytes(REQB, 5);    // 发送REQB
    memcpy(PUPI, abtRx + 1, 4); // 复制ATQB的PUIP
    printf("PUPI: ");
    print\_hex(PUPI, 4);

    uint8\_t Attrib\[11\] = {0x1d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0x01, 0x08};
    memcpy(Attrib \+ 1, PUPI, 4);
    iso14443b\_crc\_append(Attrib, 9);
    transmit\_bytes(Attrib, 11); // 发送ATTRIB
    uint8\_t ReadGUID\[7\] = {0x00, 0x36, 0x00, 0x00, 0x08};
    iso14443b\_crc\_append(ReadGUID, 5);
    transmit\_bytes(ReadGUID, 7); // 发送读取UID命令
    nfc\_close(pnd);
    nfc\_exit(context);
    exit(EXIT\_SUCCESS);
}

[![复制代码](//assets.cnblogs.com/images/copycode.gif)](javascript:void(0); "复制代码")

文章参考
----

[贴一个PN532 读取二代证 UID 的完整C程序 (amobbs.com 阿莫电子论坛 - 东莞阿莫电子网站)](https://www.amobbs.com/thread-5614403-1-1.html)

[关于PN532 读取二代证 UID (amobbs.com 阿莫电子论坛 - 东莞阿莫电子网站)](https://www.amobbs.com/thread-5588921-1-1.html)

[利用PN532读取二代证UID - 雨中尘埃 - 博客园 (cnblogs.com)](https://www.cnblogs.com/rainmote/p/7518493.html)

本文转自 <https://www.cnblogs.com/pluse/p/17562053.html>，如有侵权，请联系删除。