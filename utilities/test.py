def increment_filename_extra(old_file, frequency=None):
    """
    Increments the file extension if it is numeric.  It preserves the number of
    characters in the extension.
    
    Examples:
            print increment_filename('test_001.ext',  20)
            test_f020MHz_002.ext

            print increment_filename('test_f010MHz_001.ext', 20)
            test_f020MHz_002.ext
            
            print increment_filename('test')
            test
    """
    dot = old_file.rfind('.')
    underscore = old_file.rfind('_')

    if (underscore == -1): return old_file
    if (underscore+1 == dot): return old_file

    Hz = old_file.rfind('Hz')

    if frequency is not None:
        f_str = ('%9d'%(frequency)).replace(' ', '0')
        if Hz > 5:
            f_expected = Hz - 10
            f = old_file.rfind('f',f_expected)
            if f == f_expected:
                old_file = old_file[:f+1] + f_str + old_file[f+1+9:]
        else:
            old_file = old_file[:underscore] + '_f' +f_str +'Hz'  + old_file[underscore:]
            dot = old_file.rfind('.')
            underscore = old_file.rfind('_')


    ext = old_file[dot+1:]
    n = old_file[underscore+1:dot]
    file = old_file[0:underscore]
    nc = str(len(n))
    try:
        n = int(n)+1      # Convert to number, add one, catch error
        format = '%' + nc + '.' + nc + 'd'
        n = (format % n)
        new_file = file + '_' + n + '.'+ext
        return new_file
    except:
        return old_file

print (increment_filename_extra('test_f030000000Hz_001.ext',  20000000))
print (increment_filename_extra('test_004.ext',  30000000))
print (increment_filename_extra('test_004.ext'))