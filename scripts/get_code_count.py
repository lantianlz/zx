# -*- coding: utf-8 -*-


import os


def read_line_count(fname):
    count = 0
    for file_line in open(fname).xreadlines():
        count += 1
    return count


def get_code_count():
    from pprint import pprint

    exts = ['.py', '.html', '.js', '.sh', '.txt', '.css']
    fcount = {}
    flist = {}
    all_exts = []

    init_path = os.getcwd()
    init_path = os.path.abspath(os.path.join(init_path, '../'))
    for root, dirs, files in os.walk(init_path):
        # 隐藏目录剔除
        if '.git' in root:
            # print '%s pass' % root
            continue

        for f in files:
            if '.' in f:
                ext = '.%s' % f.rsplit('.', 1)[1]
                if not ext in all_exts:
                    all_exts.append(ext)

                fname = (root + '/' + f)
                # ext = f[f.rindex('.'):]
                if ext in exts:
                    c = read_line_count(fname)
                    if ext in fcount:
                        fcount[ext][0] += 1
                        fcount[ext][1] += c
                        flist[ext].append([fname, c])
                    else:
                        fcount[ext] = [1, c]
                        flist[ext] = [[fname, c]]

    print 'all file ext is:%s' % all_exts
    print 'file count:'
    pprint(fcount)
    # print 'file list is:'
    for key in flist:
        flist[key].sort(key=lambda x: x[1], reverse=True)
    # pprint(flist)


if __name__ == '__main__':
    get_code_count()
