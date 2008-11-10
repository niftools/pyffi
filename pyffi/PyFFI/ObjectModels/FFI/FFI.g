grammar FFI;

options {
    // PYTHON
    language = Python;
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
}

// JAVA 
/*
@lexer::members {
    // current indentation level
    int current_indent = 0;
}
*/
// PYTHON
// note: ANTLR defines Python members on class level, but we want to define an
//       instance variable, not a class variable, hence it must go in __init__
//       so we declare the member in __init__
@lexer::init {
    # current indentation level
    self.current_indent = 0
}


/*------------------------------------------------------------------
 * PARSER RULES
 *------------------------------------------------------------------*/

ffi
    :   formatdef typeblock?
    ;

formatdef
    :   'fileformat' FORMATNAME NEWLINE
    ;

typeblock
    :   'type' COLON INDENT (typedef NEWLINE)* typedef DEDENT
    ;

typedef
    :   TYPENAME // basic type
    |   TYPENAME '=' TYPENAME // alias
    ;

/*------------------------------------------------------------------
 * LEXER RULES
 *------------------------------------------------------------------*/

// whitespace and comments


COMMENT
    :   '#' ~('\n')* '\n' {$channel=HIDDEN;}
    ;

fragment
DIGIT   :   '0'..'9'
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

// lower_case_with_underscores for attribute names
ATTRIBUTENAME
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

// note: emits INDENT and DEDENT instead of NEWLINE if indentation changes
NEWLINE
// JAVA
/*
@init {
    int indent = 0;
}
*/
// PYTHON
@init {
    indent = 0
}
    :   // ignore whitespace at end of line, lines that only consist of whitespace
        ((('\f')? ('\r')? '\n') | ' ')*
        // but we need of course at least one real newline
        (('\f')? ('\r')? '\n')
        // eat indentation, and count it
        ('    '
            // JAVA
            /*
            {
                indent++;
            }
            */
            // PYTHON
            {
                indent += 1
            }
        )*
            // indentation increased by one level: emit INDENT
        // indentation remained the same: emit NEWLINE
        // indentation decreased (by any level): emit DEDENT as many as there are levels
        // JAVA
        /*
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
                throw new RuntimeException("bad indentation")
            }
        }
        */
        // PYTHON
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

// ignore whitespace
WS
    : (' ')+ { $channel=HIDDEN; }
    ;

