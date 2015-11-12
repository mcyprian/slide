import sys
import pprint

pp = pprint.PrettyPrinter()

class Map_vars(object):

    def __init__(self, preds1, preds2, top_call1, top_call2):
        '''
        Maps ekvivalent variables in predicates
        '''
        print "Top call 1:"
        pp.pprint(top_call1)
        print "Preds 1:"
        pp.pprint(preds1)
        print "Top call 2:"
        pp.pprint(top_call2)
        print "Preds 2:"
        pp.pprint(preds2)
        print("\n")
        self.expand(top_call1, preds1['P2'])
        self.pred_new = []
        sys.exit(1)

    def expand(self, call, pred):
        args = dict(zip(pred[0], call[0][1]))
        self.recursive_iter(pred, args)
    
    def recursive_iter(self, obj, args):
        if not isinstance(obj, str):
            for index, item in enumerate(obj):
                if hasattr(obj, '__iter__'):
                    self.recursive_iter(item, args)
        if obj in args.keys():
            print("TO ASIGN {}".format(args[obj]))
        


