def formatSize(bytes):
    try:
        bytes = float(bytes)
        kb = bytes / 1024
    except:
        print("传入的字节格式不对")
        return "Error"

    if kb >= 1024:
        M = kb / 1024
        if M >= 1024:
            G = M / 1024
            return "%0.2fG" % (G)
        else:
            return "%0.2fM" % (M)
    else:
        return "%0.2fkb" % (kb)