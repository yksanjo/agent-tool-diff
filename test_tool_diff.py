import copy
import tempfile
import unittest
from pathlib import Path
from tool_diff import compare,inventory,load

BASE={'tools':[{'name':'fixture_read','description':'Read synthetic data','inputSchema':{'type':'object','properties':{'id':{'type':'string'}}}}]}
class Tests(unittest.TestCase):
    def setUp(self): self.new=copy.deepcopy(BASE)
    def test_unchanged(self):self.assertFalse(compare(BASE,self.new)['review_required'])
    def test_added(self):
        self.new['tools'].append({'name':'fixture_write','inputSchema':{}})
        self.assertEqual(compare(BASE,self.new)['added'],['fixture_write'])
    def test_removed(self):self.assertEqual(compare(BASE,{'tools':[]})['removed'],['fixture_read'])
    def test_description(self):
        self.new['tools'][0]['description']='Changed text'
        self.assertEqual(compare(BASE,self.new)['changed'][0]['fields'],['description'])
    def test_schema(self):
        self.new['tools'][0]['inputSchema']['required']=['id']
        self.assertEqual(compare(BASE,self.new)['changed'][0]['fields'],['inputSchema'])
    def test_extension(self):
        self.new['tools'][0]['annotations']={'readOnlyHint':False}
        self.assertEqual(compare(BASE,self.new)['changed'][0]['fields'],['annotations'])
    def test_duplicate_names(self):
        self.new['tools']*=2
        with self.assertRaises(ValueError):inventory(self.new)
    def test_invalid(self):
        for item in [{},{'tools':None},{'tools':[{'name':[],'inputSchema':{}}]}]:
            with self.assertRaises(ValueError):inventory(item)
    def test_key_order(self):
        self.new['tools'][0]=dict(reversed(list(self.new['tools'][0].items())))
        self.assertFalse(compare(BASE,self.new)['review_required'])
    def test_tool_order(self):
        a={'name':'second','inputSchema':{}}
        self.assertFalse(compare({'tools':[a,BASE['tools'][0]]},{'tools':[BASE['tools'][0],a]})['review_required'])
    def test_null_vs_missing(self):
        self.new['tools'][0]['extension']=None
        self.assertEqual(compare(BASE,self.new)['changed'][0]['fields'],['extension'])
    def test_duplicate_json(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.json';p.write_text('{"tools":[],"tools":[]}')
            with self.assertRaises(ValueError):load(p)

if __name__=='__main__':unittest.main()
