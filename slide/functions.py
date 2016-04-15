# Adam Rogalewicz
# 
# SL to TA
# distrubuted under GNU GPL licence

# Global function
import tempfile

class FunctionError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def keyfce(x):
    for outer_index, item in enumerate(x):
        if isinstance(item, int):
            x[index] = str(item)
        elif isinstance(item, list):
            for inner_index, inner_item in enumerate(item):
                if isinstance(inner_item, int):
                    item[inner_index] = str(inner_item)
    return x

def numbers_back(sorted_list):
    for x in sorted_list:
        for outer_index, item in enumerate(x):
            if isinstance(item, str) and item.isdigit():
                x[index] = int(item)
            elif isinstance(item, list):
                for inner_index, inner_item in enumerate(item):
                    if isinstance(inner_item, str) and inner_item.isdigit():
                        item[inner_index] = int(inner_item)
    return sorted_list


def paralel_sort(a,b):
    # sort field a and in parallel do the equal manipulations with the list b
    if not(len(a)==len(b)):
        raise RotateError("arity of tile does not correspond to arity of rule")
    tmp=[]
    for x in range(0,len(a)):
        tmp=tmp+[(a[x],b[x])]
    tmp=sorted(tmp, key=keyfce)
    tmp = numbers_back(tmp)
    a=[]
    b=[]
    for x in tmp:
        a=a+[x[0]]
        b=b+[x[1]]
    return (a,b)

def tile_index(tile,tiles_list):
    # return an index to the list of tiles
    # if the tile is not in the list, then add it and return the index
    if tile in tiles_list:
        symbol=tiles_list.index(tile)
    else:
        symbol=len(tiles_list)
        tiles_list.append(tile)
    return symbol

def tile_normalize(tile):
    # this is needed in the case allowed of extra edges
    # one has to normalize the sets x^eq_{-1} ... x^{eq}_k in such a way, that
    # 'al' = variable allocated
    # 'sX' = variable pointed by selector X
    # 'eX' = equivalence variable no. X
    # variable eX are ordered in a canonical way e1,e2,e3,... starting from x^{eq}_{-1}
    (a,b,c,d)=tile
    order={}
    counter=1
    a_new=[]
    for xset in a:
        xset_new=[]
        tmp=0
        for el in xset:
            if isinstance(el,int):
                if tmp:
                    # this line should be unaccesible if everything works in a right way
                    raise FunctionError("mixture of x^{fw} and x^{eq}")
                xset_new.append(el)
                continue
            tmp=1
            if el=="al" or el[0]=='s':
                # alocated node and selectors are unique, no need to normalize
                xset_new.append(el)
                continue
            if el in order.keys():
                (nvar,num)=order[el]
                if num>=2:
                    print(tile)
                    raise FunctionError("equality variable %s occurs more then twice in the tile"%el)
                order[el]=(nvar,num+1)
                xset_new.append(nvar)

            else:
                nvar="e%i"%counter
                order[el]=(nvar,1)
                counter=counter+1
                xset_new.append(nvar)
        a_new.append(xset_new)
    # check, that there are no death equality variables
    for key in order.keys():

        (nvar,num)=order[key]
        if not (num==2):
            raise FunctionError("equality variable %s occurs only once = DEATH variable"%key)
            
    return((a_new,b,c,d))

def get_tmp_filename():
    tmp=tempfile.NamedTemporaryFile(delete=False)
    tmpfilename=tmp.name
    tmp.close()
    return tmpfilename

                




