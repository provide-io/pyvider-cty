# tests/values/test_cty_values_base.py
from pyvider.cty import CtyString, CtyNumber, CtyBool, CtyValue
from pyvider.cty.marks import CtyMark

class TestCtyValueBasicOperations:
    def test_value_creation_and_access(self):
        str_type = CtyString()
        str_val = str_type.validate("hello")
        assert str_val.value == "hello"
        assert str_val.type.equal(str_type)

    def test_value_marks(self):
        num_val = CtyNumber().validate(123)
        marked_val = num_val.mark(CtyMark("sensitive"))
        
        assert not num_val.has_mark(CtyMark("sensitive"))
        assert marked_val.has_mark(CtyMark("sensitive"))
        
        unmarked_val, marks = marked_val.unmark()
        assert not unmarked_val.has_mark(CtyMark("sensitive"))
        assert len(marks) == 1
        assert CtyMark("sensitive") in marks
