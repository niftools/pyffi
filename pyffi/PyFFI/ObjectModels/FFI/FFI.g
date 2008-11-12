grammar FFI;

options {
    //language = Python;
    output=AST;
    ASTLabelType=CommonTree;
}

tokens {
    // emitted when indentation increases
    // see NEWLINE for details
    INDENT;
    // emitted when indentation decreases
    // see NEWLINE for details
    DEDENT;
    // keywords
    CLASS='class';
    FILEFORMAT='fileformat';
    TYPE='type';
}

// target specific code
// ====================

// current_indent: lexer variable which measures the current indentation level
// NEWLINE: special lexer token which works as follows
//    indentation increased by one level: emit INDENT
//    indentation remained the same: emit NEWLINE
//    indentation decreased (by any level): emit DEDENT as many as decreased

// JAVA

/* */

@lexer::members {
    int current_indent = 0;
}

NEWLINE
@init {
    int indent = 0;
}
    :
        ((('\f')? ('\r')? '\n') | ' ')*
        (('\f')? ('\r')? '\n')
        ('    '
            {
                indent++;
            }
        )*
        {
            if (indent == current_indent + 1) {
                current_indent++;
                emit(new ClassicToken(INDENT, ">"));
            }
            else if (indent == current_indent) {
                emit(new ClassicToken(NEWLINE, "\n"));
            }
            else if (indent < current_indent) {
                while (indent < current_indent) {
                    current_indent--;
                    emit(new ClassicToken(DEDENT, "<"));
                }
            }
            else {
                throw new RuntimeException("bad indentation");
            }
        }
    ;

/* */

// PYTHON
// note: ANTLR defines Python members on class level, but we want to define an
//       instance variable, not a class variable, hence it must go in __init__
//       so we declare the member in __init__

/*

@lexer::init {
    self.current_indent = 0
}

NEWLINE
@init {
    indent = 0
}
    :
        ((('\f')? ('\r')? '\n') | ' ')*
        (('\f')? ('\r')? '\n')
        ('    '
            {
                indent += 1
            }
        )*
        {   
            if (indent == self.current_indent + 1):
                self.current_indent += 1
                self.emit(ClassicToken(INDENT, ">"))
            elif indent == self.current_indent:
                self.emit(ClassicToken(NEWLINE, "\n"))
            elif indent < self.current_indent:
                while indent < self.current_indent:
                    self.current_indent -= 1
                    self.emit(ClassicToken(DEDENT, "<"))
            else:
                raise RuntimeError("bad indentation")
        }
    ;

*/

/*------------------------------------------------------------------
 * PARSER RULES
 *------------------------------------------------------------------*/

ffi
    :   formatdef typeblock? classblock* EOF
    ;

formatdef
    :   longdoc? FILEFORMAT FORMATNAME SHORTDOC? NEWLINE
    ;

typeblock
    :   TYPE COLON INDENT (typedef NEWLINE)* typedef DEDENT
    ;

typedef
    :   longdoc? TYPENAME SHORTDOC? // basic type
    |   longdoc? TYPENAME '=' TYPENAME SHORTDOC? // alias
    ;

classblock
    :    longdoc? CLASS TYPENAME COLON SHORTDOC? INDENT (fielddef NEWLINE)* fielddef DEDENT    
    ;

fielddef
    :    longdoc? TYPENAME VARIABLENAME SHORTDOC?
    ;

// documentation preceeding a definition, with newlines
longdoc
    :   (SHORTDOC NEWLINE)+
    ;

/*------------------------------------------------------------------
 * LEXER RULES
 *------------------------------------------------------------------*/

// whitespace and comments

// documentation following a definition, no newline
// (on the same line of the definition)
SHORTDOC
    :   '#' ~('\n')*
    ;

fragment
DIGIT
    :   '0'..'9'
    ;

fragment
DIGITS  :   DIGIT+
    ;

INT
    // hex
    :   '0x' ( '0' .. '9' | 'a' .. 'f' | 'A' .. 'F' )+
    // octal
    |   '0o' ( '0' .. '7')+
    // binary
    |   '0b' ( '0' .. '1')+
    // decimal
    |   DIGITS+
    ;

fragment
EXPONENT
    :    'e' ( '+' | '-' )? DIGITS
    ;

FLOAT
    :   DIGITS '.' DIGITS EXPONENT?
    ;

COLON
    :   ':'
    ;

fragment
LCLETTER:   'a'..'z'
    ;

fragment
UCLETTER:   'A'..'Z'
    ;

// UPPERCASE for format name

FORMATNAME
    :   UCLETTER (UCLETTER | DIGITS)*
    ;

// lower_case_with_underscores for variable names (e.g. fields)
VARIABLENAME
    :   LCLETTER (LCLETTER | DIGITS | '_')*
    ;

// CamelCase for type names
TYPENAME
    :   UCLETTER (LCLETTER | UCLETTER | DIGITS)*
    ;

STRING
    :   '"' (ESC|~('\\'|'\n'|'"'))* '"'
    ;

fragment
ESC
    :   '\\' .
    ;

// ignore whitespace
WS
    :   (' ')+ { $channel=HIDDEN; }
    ;
