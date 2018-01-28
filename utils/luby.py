def luby(index):
    """
    implementation of https://pdfs.semanticscholar.org/2d0e/4df4de47ec38a2da161a850fd62164e62864.pdf
    stolen from https://github.com/dddejan/CVC4/blob/mcsat-fmcad2013/src/mcsat/bcp/bcp_engine.cpp#L254
    """
    size = 1
    maxPower = 0
    while (size <= index):
        size = 2 * size + 1
        maxPower += 1
    while (size > index + 1):
        size = size // 2
        maxPower -= 1
        if (size <= index):
            index -= size
    return maxPower
