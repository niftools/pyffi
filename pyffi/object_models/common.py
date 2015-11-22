"""Implements common basic types in XML file format descriptions."""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2012, Python File Format Interface.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * Neither the name of the Python File Format Interface
#      project nor the names of its contributors may be used to endorse
#      or promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ***** END LICENSE BLOCK *****

import struct
import logging

from pyffi.object_models.xml.basic import BasicBase
from pyffi.object_models.editable import EditableSpinBox
from pyffi.object_models.editable import EditableFloatSpinBox
from pyffi.object_models.editable import EditableLineEdit
from pyffi.object_models.editable import EditableBoolComboBox

# TODO get rid of these
_b = b''
_b00 = b'\x00'

def _as_bytes(value):
    """Helper function which converts a string to bytes (this is useful for
    set_value in all string classes, which use bytes for representation).

    :return: The bytes representing the value.
    :rtype: C{bytes}

    >>> _as_bytes("\\u00e9defa") == "\\u00e9defa".encode("utf-8")
    True

    >>> _as_bytes(123) # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    TypeError: ...
    """
    if isinstance(value, str):
        return value.encode("utf-8", "replace")
    elif isinstance(value, bytes):
        return value
    else:
        raise TypeError("expected str")

def _as_str(value):
    """Helper function to convert bytes back to str. This is used in
    the __str__ functions for simple string types. If you want a custom
    encoding, use an explicit decode call on the value.
    """
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    elif isinstance(value, str):
        return value
    else:
        raise TypeError("expected bytes")

class Int(BasicBase, EditableSpinBox):
    """Basic implementation of a 32-bit signed integer type. Also serves as a
    base class for all other integer types. Follows specified byte order.

    >>> from tempfile import TemporaryFile
    >>> tmp = TemporaryFile()
    >>> from pyffi.object_models import FileFormat
    >>> data = FileFormat.Data()
    >>> i = Int()
    >>> i.set_value(-1)
    >>> i.get_value()
    -1
    >>> i.set_value(0x11223344)
    >>> i.write(tmp, data)
    >>> j = Int()
    >>> if tmp.seek(0): pass # ignore result for py3k
    >>> j.read(tmp, data)
    >>> hex(j.get_value())
    '0x11223344'
    >>> i.set_value(2**40) # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    ValueError: ...
    >>> i.set_value('hello world')
    Traceback (most recent call last):
        ...
    ValueError: cannot convert value 'hello world' to integer
    >>> if tmp.seek(0): pass # ignore result for py3k
    >>> if tmp.write('\x11\x22\x33\x44'.encode("ascii")): pass # b'\x11\x22\x33\x44'
    >>> if tmp.seek(0): pass # ignore result for py3k
    >>> i.read(tmp, data)
    >>> hex(i.get_value())
    '0x44332211'
    """

    _min = -0x80000000 #: Minimum value.
    _max = 0x7fffffff  #: Maximum value.
    _struct = 'i'      #: Character used to represent type in struct.
    _size = 4          #: Number of bytes.

    def __init__(self, **kwargs):
        """Initialize the integer."""
        super(Int, self).__init__(**kwargs)
        self._value = 0

    def get_value(self):
        """Return stored value.

        :return: The stored value.
        """
        return self._value

    def set_value(self, value):
        """Set value to C{value}. Calls C{int(value)} to convert to integer.

        :param value: The value to assign.
        :type value: int
        """
        try:
            val = int(value)
        except ValueError:
            try:
                val = int(value, 16) # for '0x...' strings
            except ValueError:
                try:
                    val = getattr(self, value) # for enums
                except AttributeError:
                    raise ValueError(
                        "cannot convert value '%s' to integer"%value)
        if val < self._min or val > self._max:
            raise ValueError('value out of range (%i)' % val)
        self._value = val

    def read(self, stream, data):
        """Read value from stream.

        :param stream: The stream to read from.
        :type stream: file
        """
        self._value = struct.unpack(data._byte_order + self._struct,
                                    stream.read(self._size))[0]

    def write(self, stream, data):
        """Write value to stream.

        :param stream: The stream to write to.
        :type stream: file
        """
        stream.write(struct.pack(data._byte_order + self._struct, self._value))

    def __str__(self):
        return str(self.get_value())

    @classmethod
    def get_size(cls, data=None):
        """Return number of bytes this type occupies in a file.

        :return: Number of bytes.
        """
        return cls._size

    def get_hash(self, data=None):
        """Return a hash value for this value.

        :return: An immutable object that can be used as a hash.
        """
        return self.get_value()

    def get_editor_minimum(self):
        """Minimum possible value.

        :return: Minimum possible value.
        """
        return self._min

    def get_editor_maximum(self):
        """Maximum possible value.

        :return: Maximum possible value.
        """
        return self._max

class UInt(Int):
    """Implementation of a 32-bit unsigned integer type."""
    _min = 0
    _max = 0xffffffff
    _struct = 'I'
    _size = 4

class Int64(Int):
    """Implementation of a 64-bit signed integer type."""
    _min = -0x8000000000000000
    _max = 0x7fffffffffffffff
    _struct = 'q'
    _size = 8

class UInt64(Int):
    """Implementation of a 64-bit unsigned integer type."""
    _min = 0
    _max = 0xffffffffffffffff
    _struct = 'Q'
    _size = 8

class Byte(Int):
    """Implementation of a 8-bit signed integer type."""
    _min = -0x80
    _max = 0x7f
    _struct = 'b'
    _size = 1

class UByte(Int):
    """Implementation of a 8-bit unsigned integer type."""
    _min = 0
    _max = 0xff
    _struct = 'B'
    _size = 1

class Short(Int):
    """Implementation of a 16-bit signed integer type."""
    _min = -0x8000
    _max = 0x7fff
    _struct = 'h'
    _size = 2

class UShort(UInt):
    """Implementation of a 16-bit unsigned integer type."""
    _min = 0
    _max = 0xffff
    _struct = 'H'
    _size = 2

class ULittle32(UInt):
    """Little endian 32 bit unsigned integer (ignores specified data
    byte order).
    """
    def read(self, stream, data):
        """Read value from stream.

        :param stream: The stream to read from.
        :type stream: file
        """
        self._value = struct.unpack('<' + self._struct,
                                    stream.read(self._size))[0]

    def write(self, stream, data):
        """Write value to stream.

        :param stream: The stream to write to.
        :type stream: file
        """
        stream.write(struct.pack('<' + self._struct, self._value))

class Bool(UByte, EditableBoolComboBox):
    """Simple bool implementation."""

    def get_value(self):
        """Return stored value.

        :return: The stored value.
        """
        return bool(self._value)

    def set_value(self, value):
        """Set value to C{value}.

        :param value: The value to assign.
        :type value: bool
        """
        self._value = 1 if value else 0

class Char(BasicBase, EditableLineEdit):
    """Implementation of an (unencoded) 8-bit character."""

    def __init__(self, **kwargs):
        """Initialize the character."""
        super(Char, self).__init__(**kwargs)
        self._value = b'\x00'

    def get_value(self):
        """Return stored value.

        :return: The stored value.
        """
        return self._value

    def set_value(self, value):
        """Set character to C{value}.

        :param value: The value to assign (bytes of length 1).
        :type value: bytes
        """
        assert(isinstance(value, bytes))
        assert(len(value) == 1)
        self._value = value

    def read(self, stream, data):
        """Read value from stream.

        :param stream: The stream to read from.
        :type stream: file
        """
        self._value = stream.read(1)

    def write(self, stream, data):
        """Write value to stream.

        :param stream: The stream to write to.
        :type stream: file
        """
        stream.write(self._value)

    def __str__(self):
        return _as_str(self._value)

    def get_size(self, data=None):
        """Return number of bytes this type occupies in a file.

        :return: Number of bytes.
        """
        return 1

    def get_hash(self, data=None):
        """Return a hash value for this value.

        :return: An immutable object that can be used as a hash.
        """
        self.get_value()

class Float(BasicBase, EditableFloatSpinBox):
    """Implementation of a 32-bit float."""

    def __init__(self, **kwargs):
        """Initialize the float."""
        super(Float, self).__init__(**kwargs)
        self._value = 0

    def get_value(self):
        """Return stored value.

        :return: The stored value.
        """
        return self._value

    def set_value(self, value):
        """Set value to C{value}.

        :param value: The value to assign.
        :type value: float
        """
        self._value = float(value)

    def read(self, stream, data):
        """Read value from stream.

        :param stream: The stream to read from.
        :type stream: file
        """
        self._value = struct.unpack(data._byte_order + 'f',
                                    stream.read(4))[0]

    def write(self, stream, data):
        """Write value to stream.

        :param stream: The stream to write to.
        :type stream: file
        """
        try:
            stream.write(struct.pack(data._byte_order + 'f',
                                     self._value))
        except OverflowError:
            logger = logging.getLogger("pyffi.object_models")
            logger.warn("float value overflow, writing NaN")
            stream.write(struct.pack(data._byte_order + 'I',
                                     0x7fc00000))

    def get_size(self, data=None):
        """Return number of bytes this type occupies in a file.

        :return: Number of bytes.
        """
        return 4

    def get_hash(self, data=None):
        """Return a hash value for this value. Currently implemented
        with precision 1/200.

        :return: An immutable object that can be used as a hash.
        """
        return int(self.get_value()*200)


class HFloat(Float, EditableFloatSpinBox):
    """Implementation of a 16-bit float."""

    def __init__(self, **kwargs):
        """Initialize the float."""
        super(HFloat, self).__init__(**kwargs)
        self._value = float()

    @staticmethod
    def toFloatFast(bom, value):
        exponent = value & 0x00007C00
        mantissa = value & 0x3ff
        if not exponent: return float()
        bits = ((value & 32768) << 16) | \
               ((exponent + 0x0001C000) | mantissa) << 13
        return struct.unpack(bom+"f", struct.pack(bom+"I", bits))[0]

    @staticmethod
    def fromFloatFast(bom, value):
        if value > 131008.000:
            bits = 0x47FFE000
        else:
            bits = struct.unpack(bom+"I", struct.pack(bom+"f", value))[0]
        if (bits & 0x7FFFFFFF) < 0x38800000: return int()
        result = ((bits + 0x48000000) & ~0x3ff) | (bits & 0x3ff)
        return ((result >> 13) & 0xFFFF) | ((bits & 0x80000000) >> 16)

    @staticmethod
    def half_sub( ha, hb ):
        return half_add( ha, hb ^ 0x8000 );

    @staticmethod
    def h_sels( test, a, b ):
        mask = test >> 31
        return (a & mask) | (b & ~mask)

    @staticmethod
    def h_selb( mask, a, b ):
        return (a & b) | (b & ~mask)

    @staticmethod
    def h_cntlz( x ):
        x1  =   x  | (x >> 1)
        x2  =   x1 >> 2
        x3  =   x1 | x2
        x4  =   x3 >> 4
        x5  =   x3 | x4
        x6  =   x5 >> 8
        x7  =   x5 | x6
        x8  =   x7 >> 16
        x9  =    x7 | x8
        xA  =  ~x9
        xB  =   xA >> 1
        xC  =   xB & 0x55555555
        xD  =   xA - xC
        xE  =   xD & 0x33333333
        xF  =   xD >> 2
        x10 =   xF & 0x33333333
        x11 =   xE + x10
        x12 =   x11 >> 4
        x13 =   x11 + x12
        x14 =   x13 & 0x0f0f0f0f
        x15 =   x14 >> 8
        x16 =   x14 + x15
        x19 =   (x16 + (x16 >> 16)) & 0x0000003f
        return ( x19 )

    @staticmethod
    def toFloatAccurate(bom, value):
        h                     = int(value)
        h_e_mask              = 0x00007c00
        h_m_mask              = 0x000003ff
        h_s_mask              = 0x00008000
        h_f_s_pos_offset      = 0x00000010
        h_f_e_pos_offset      = 0x0000000d
        h_f_bias_offset       = 0x0001c000
        f_e_mask              = 0x7f800000
        f_m_mask              = 0x007fffff
        h_f_e_denorm_bias     = 0x0000007e
        h_f_m_denorm_sa_bias  = 0x00000008
        f_e_pos               = 0x00000017
        h_e_mask_minus_one    = 0x00007bff
        h_e                   = h & h_e_mask;
        h_m                   = h & h_m_mask
        h_s                   = h & h_s_mask
        h_e_f_bias            = h_e + h_f_bias_offset
        h_m_nlz               = HFloat.h_cntlz( h_m )
        f_s                   = h_s << h_f_s_pos_offset
        f_e                   = h_e_f_bias << h_f_e_pos_offset
        f_m                   = h_m << h_f_e_pos_offset
        f_em                  = f_e | f_m
        h_f_m_sa              = h_m_nlz - h_f_m_denorm_sa_bias
        f_e_denorm_unpacked   = h_f_e_denorm_bias -   h_f_m_sa
        h_f_m                 = h_m << h_f_m_sa if h_m else 0
        f_m_denorm            = h_f_m & f_m_mask
        f_e_denorm            = f_e_denorm_unpacked << f_e_pos
        f_em_denorm           = f_e_denorm | f_m_denorm
        f_em_nan              = f_e_mask | f_m
        is_e_eqz_msb          = h_e - 1
        is_m_nez_msb          = -h_m
        is_e_flagged_msb      = h_e_mask_minus_one - h_e
        is_zero_msb           = is_e_eqz_msb & ~is_m_nez_msb
        is_inf_msb            = is_e_flagged_msb & ~is_m_nez_msb
        is_denorm_msb         = is_m_nez_msb & is_e_eqz_msb
        is_nan_msb            = is_e_flagged_msb & is_m_nez_msb
        is_zero               = is_zero_msb >> 31
        f_zero_result         = f_em & ~is_zero
        f_denorm_result       = HFloat.h_sels( is_denorm_msb, f_em_denorm, f_zero_result  )
        f_inf_result          = HFloat.h_sels( is_inf_msb,    f_e_mask,    f_denorm_result)
        f_nan_result          = HFloat.h_sels( is_nan_msb,    f_em_nan,    f_inf_result   )
        f_result              = f_s | f_nan_result
        return struct.unpack(bom+"f", struct.pack(bom+"I", f_result))[0]

    @staticmethod
    def fromFloatAccurate(bom, value):
        f                          = struct.unpack(bom+"I", struct.pack(bom+"f", value))[0]
        one                        = 0x00000001
        f_s_mask                   = 0x80000000
        f_e_mask                   = 0x7f800000
        f_m_mask                   = 0x007fffff
        f_m_hidden_bit             = 0x00800000
        f_m_round_bit              = 0x00001000
        f_snan_mask                = 0x7fc00000
        f_e_pos                    = 0x00000017
        h_e_pos                    = 0x0000000a
        h_e_mask                   = 0x00007c00
        h_snan_mask                = 0x00007e00
        h_e_mask_value             = 0x0000001f
        f_h_s_pos_offset           = 0x00000010
        f_h_bias_offset            = 0x00000070
        f_h_m_pos_offset           = 0x0000000d
        h_nan_min                  = 0x00007c01
        f_h_e_biased_flag          = 0x0000008f
        f_s                        =  f & f_s_mask
        f_e                        =  f & f_e_mask
        h_s                        =  f_s >> f_h_s_pos_offset
        f_m                        =  f & f_m_mask
        f_e_amount                 =  f_e >> f_e_pos
        f_e_half_bias              =  f_e_amount - f_h_bias_offset
        f_snan                     =  f & f_snan_mask
        f_m_round_mask             =  f_m & f_m_round_bit
        f_m_round_offset           =  f_m_round_mask <<  one
        f_m_rounded                =  f_m + f_m_round_offset
        f_m_denorm_sa              =  one - f_e_half_bias
        f_m_with_hidden            =  f_m_rounded | f_m_hidden_bit
        f_m_denorm                 =  f_m_with_hidden >> f_m_denorm_sa if f_m_denorm_sa >= 0 else 0
        h_m_denorm                 =  f_m_denorm >> f_h_m_pos_offset
        f_m_rounded_overflow       =  f_m_rounded & f_m_hidden_bit
        m_nan                      =  f_m >> f_h_m_pos_offset
        h_em_nan                   =  h_e_mask | m_nan
        h_e_norm_overflow_offset   =  f_e_half_bias + 1
        h_e_norm_overflow          =  h_e_norm_overflow_offset << h_e_pos
        h_e_norm                   =  f_e_half_bias << h_e_pos
        h_m_norm                   =  f_m_rounded >> f_h_m_pos_offset
        h_em_norm                  =  h_e_norm | h_m_norm
        is_h_ndenorm_msb           =  f_h_bias_offset - f_e_amount
        is_f_e_flagged_msb         =  f_h_e_biased_flag - f_e_half_bias
        is_h_denorm_msb            = ~is_h_ndenorm_msb
        is_f_m_eqz_msb             =  f_m   - 1
        is_h_nan_eqz_msb           =  m_nan - 1
        is_f_inf_msb               =  is_f_e_flagged_msb & is_f_m_eqz_msb
        is_f_nan_underflow_msb     =  is_f_e_flagged_msb & is_h_nan_eqz_msb
        is_e_overflow_msb          =  h_e_mask_value - f_e_half_bias
        is_h_inf_msb               =  is_e_overflow_msb |  is_f_inf_msb
        is_f_nsnan_msb             =  f_snan - f_snan_mask
        is_m_norm_overflow_msb     = -f_m_rounded_overflow
        is_f_snan_msb              = ~is_f_nsnan_msb
        h_em_overflow_result       = HFloat.h_sels( is_m_norm_overflow_msb, h_e_norm_overflow, h_em_norm                 )
        h_em_nan_result            = HFloat.h_sels( is_f_e_flagged_msb,     h_em_nan,          h_em_overflow_result      )
        h_em_nan_underflow_result  = HFloat.h_sels( is_f_nan_underflow_msb, h_nan_min,         h_em_nan_result           )
        h_em_inf_result            = HFloat.h_sels( is_h_inf_msb,           h_e_mask,          h_em_nan_underflow_result )
        h_em_denorm_result         = HFloat.h_sels( is_h_denorm_msb,        h_m_denorm,        h_em_inf_result           )
        h_em_snan_result           = HFloat.h_sels( is_f_snan_msb,          h_snan_mask,       h_em_denorm_result        )
        h_result                   =  h_s | h_em_snan_result
        return  h_result

    toFloat = toFloatAccurate

    fromFloat = fromFloatAccurate

    def read(self, stream, data):
        """Read value from stream.

        :param stream: The stream to read from.
        :type stream: file
        """
        bom = data._byte_order
        boi = bom + "H"
        self._value = HFloat.toFloat(bom, struct.unpack(boi,stream.read(2))[0])

    def write(self, stream, data):
        """Write value to stream.

        :param stream: The stream to write to.
        :type stream: file
        """
        bom = data._byte_order
        boi = bom + "H"
        try:
            stream.write(struct.pack(boi, HFloat.fromFloat(bom, self._value)))
        except OverflowError:
            logger = logging.getLogger("pyffi.object_models")
            logger.warn("float value overflow, writing NaN")
            stream.write(struct.pack(boi, 0x7fff))

    def get_size(self, data=None):
        """Return number of bytes this type occupies in a file.

        :return: Number of bytes.
        """
        return 2

    def get_hash(self, data=None):
        """Return a hash value for this value. Currently implemented
        with the short form.

        :return: An immutable object that can be used as a hash.
        """
        return HFloat.fromFloat(self.get_value())

class ZString(BasicBase, EditableLineEdit):
    """String of variable length (null terminated).

    >>> from tempfile import TemporaryFile
    >>> f = TemporaryFile()
    >>> s = ZString()
    >>> if f.write('abcdefghijklmnopqrst\\x00'.encode("ascii")): pass # b'abc...'
    >>> if f.seek(0): pass # ignore result for py3k
    >>> s.read(f)
    >>> str(s)
    'abcdefghijklmnopqrst'
    >>> if f.seek(0): pass # ignore result for py3k
    >>> s.set_value('Hi There!')
    >>> s.write(f)
    >>> if f.seek(0): pass # ignore result for py3k
    >>> m = ZString()
    >>> m.read(f)
    >>> str(m)
    'Hi There!'
    """
    _maxlen = 1000 #: The maximum length.

    def __init__(self, **kwargs):
        """Initialize the string."""
        super(ZString, self).__init__(**kwargs)
        self._value = b''

    def __str__(self):
        return _as_str(self._value)

    def get_value(self):
        """Return the string.

        :return: The stored string.
        :rtype: C{bytes}
        """
        return _as_str(self._value)

    def set_value(self, value):
        """Set string to C{value}.

        :param value: The value to assign.
        :type value: ``str`` (will be encoded as default) or C{bytes}
        """
        val = _as_bytes(value)
        i = val.find(b'\x00')
        if i != -1:
            val = val[:i]
        if len(val) > self._maxlen:
            raise ValueError('string too long')
        self._value = val

    def read(self, stream, data=None):
        """Read string from stream.

        :param stream: The stream to read from.
        :type stream: file
        """
        i = 0
        val = b''
        char = b''
        while char != b'\x00':
            i += 1
            if i > self._maxlen:
                raise ValueError('string too long')
            val += char
            char = stream.read(1)
        self._value = val

    def write(self, stream, data=None):
        """Write string to stream.

        :param stream: The stream to write to.
        :type stream: file
        """
        stream.write(self._value)
        stream.write(b'\x00')

    def get_size(self, data=None):
        """Return number of bytes this type occupies in a file.

        :return: Number of bytes.
        """
        return len(self._value) + 1

    def get_hash(self, data=None):
        """Return a hash value for this string.

        :return: An immutable object that can be used as a hash.
        """
        return self._value

class FixedString(BasicBase, EditableLineEdit):
    """String of fixed length. Default length is 0, so you must override
    this class and set the _len class variable.

    >>> from tempfile import TemporaryFile
    >>> f = TemporaryFile()
    >>> class String8(FixedString):
    ...     _len = 8
    >>> s = String8()
    >>> _ = f.write('abcdefghij'.encode())
    >>> _ = f.seek(0)
    >>> s.read(f)
    >>> str(s)
    'abcdefgh'
    >>> _ = f.seek(0)
    >>> s.set_value('Hi There')
    >>> s.write(f)
    >>> _ = f.seek(0)
    >>> m = String8()
    >>> m.read(f)
    >>> str(m)
    'Hi There'
    """
    _len = 0

    def __init__(self, **kwargs):
        """Initialize the string."""
        super(FixedString, self).__init__(**kwargs)
        self._value = b''

    def __str__(self):
        return _as_str(self._value)

    def get_value(self):
        """Return the string.

        :return: The stored string.
        :rtype: C{bytes}
        """
        return self._value

    def set_value(self, value):
        """Set string to C{value}.

        :param value: The value to assign.
        :type value: ``str`` (encoded as default) or C{bytes}
        """
        val = _as_bytes(value)
        if len(val) > self._len:
            raise ValueError("string '%s' too long" % val)
        self._value = val

    def read(self, stream, data=None):
        """Read string from stream.

        :param stream: The stream to read from.
        :type stream: file
        """
        self._value = stream.read(self._len)
        i = self._value.find(b'\x00')
        if i != -1:
            self._value = self._value[:i]

    def write(self, stream, data=None):
        """Write string to stream.

        :param stream: The stream to write to.
        :type stream: file
        """
        stream.write(self._value.ljust(self._len, b'\x00'))

    def get_size(self, data=None):
        """Return number of bytes this type occupies in a file.

        :return: Number of bytes.
        """
        return self._len

    def get_hash(self, data=None):
        """Return a hash value for this string.

        :return: An immutable object that can be used as a hash.
        """
        return self._value

class SizedString(BasicBase, EditableLineEdit):
    """Basic type for strings. The type starts with an unsigned int which
    describes the length of the string.

    >>> from tempfile import TemporaryFile
    >>> f = TemporaryFile()
    >>> from pyffi.object_models import FileFormat
    >>> data = FileFormat.Data()
    >>> s = SizedString()
    >>> if f.write('\\x07\\x00\\x00\\x00abcdefg'.encode("ascii")): pass # ignore result for py3k
    >>> if f.seek(0): pass # ignore result for py3k
    >>> s.read(f, data)
    >>> str(s)
    'abcdefg'
    >>> if f.seek(0): pass # ignore result for py3k
    >>> s.set_value('Hi There')
    >>> s.write(f, data)
    >>> if f.seek(0): pass # ignore result for py3k
    >>> m = SizedString()
    >>> m.read(f, data)
    >>> str(m)
    'Hi There'
    """

    def __init__(self, **kwargs):
        """Initialize the string."""
        super(SizedString, self).__init__(**kwargs)
        self._value = b''

    def get_value(self):
        """Return the string.

        :return: The stored string.
        """
        return self._value

    def set_value(self, value):
        """Set string to C{value}.

        :param value: The value to assign.
        :type value: str
        """
        val = _as_bytes(value)
        if len(val) > 10000:
            raise ValueError('string too long')
        self._value = val

    def __str__(self):
        return _as_str(self._value)

    def get_size(self, data=None):
        """Return number of bytes this type occupies in a file.

        :return: Number of bytes.
        """
        return 4 + len(self._value)

    def get_hash(self, data=None):
        """Return a hash value for this string.

        :return: An immutable object that can be used as a hash.
        """
        return self.get_value()

    def read(self, stream, data):
        """Read string from stream.

        :param stream: The stream to read from.
        :type stream: file
        """
        length, = struct.unpack(data._byte_order + 'I',
                                stream.read(4))
        if length > 10000:
            raise ValueError('string too long (0x%08X at 0x%08X)'
                             % (length, stream.tell()))
        self._value = stream.read(length)

    def write(self, stream, data):
        """Write string to stream.

        :param stream: The stream to write to.
        :type stream: file
        """
        stream.write(struct.pack(data._byte_order + 'I',
                                 len(self._value)))
        stream.write(self._value)

class UndecodedData(BasicBase):
    """Basic type for undecoded data trailing at the end of a file."""
    def __init__(self, **kwargs):
        BasicBase.__init__(self, **kwargs)
        self._value = b''

    def get_value(self):
        """Return stored value.

        :return: The stored value.
        """
        return self._value

    def set_value(self, value):
        """Set value to C{value}.

        :param value: The value to assign.
        :type value: bytes
        """
        if len(value) > 16000000:
            raise ValueError('data too long')
        self._value = value

    def __str__(self):
        return '<UNDECODED DATA>'

    def get_size(self, data=None):
        """Return number of bytes the data occupies in a file.

        :return: Number of bytes.
        """
        return len(self._value)

    def get_hash(self, data=None):
        """Return a hash value for this value.

        :return: An immutable object that can be used as a hash.
        """
        return self.get_value()

    def read(self, stream, data):
        """Read data from stream. Note that this function simply
        reads until the end of the stream.

        :param stream: The stream to read from.
        :type stream: file
        """
        self._value = stream.read(-1)

    def write(self, stream, data):
        """Write data to stream.

        :param stream: The stream to write to.
        :type stream: file
        """
        stream.write(self._value)

