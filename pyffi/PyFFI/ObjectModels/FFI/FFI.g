grammar FFI;

options {
    //language=Python;
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
    ELIF='elif';
    ELSE='else';
    FILEFORMAT='fileformat';
    IF='if';
    PARAMETER='parameter';
    TYPE='type';
}

// target specific code
// ====================

// current_indent: lexer variable which measures the current indentation level
// NEWLINE: special lexer token which works as follows
//    for every new line: emit NEWLINE
//    indentation increased by one level: emit INDENT
//    indentation decreased (by any level): emit DEDENT as many as decreased

// to allow multiple tokens to be emitted by the NEWLINE lexer, the emit
// and nextToken members are customized (this is described on the ANTLR wiki)

// JAVA

/* */

@lexer::members {
    // keep track of indentation
    int current_indent = 0;
    
    // allow multiple tokens to be emitted
    // (see http://www.antlr.org/wiki/pages/viewpage.action?pageId=3604497)
    List tokens = new ArrayList();
    public void emit(Token token) {
        state.token = token;
        tokens.add(token);
    }
    public Token nextToken() {
        super.nextToken();
        if ( tokens.size()==0 ) {
            return Token.EOF_TOKEN;
        }
        return (Token)tokens.remove(0);
    }
}

NEWLINE
@init {
    int indent = 0;
}
    :
        (
            (('\f')? ('\r')? '\n'
                {
                    emit(new ClassicToken(NEWLINE, "\n"));
                }
            )
            |
            ' ')*
        (('\f')? ('\r')? '\n'
            {
                emit(new ClassicToken(NEWLINE, "\n"));
            }
        )
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
                // nothing happens, newline already emitted
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
    self.token_stack = []
}

// multiple tokens per lexical symbol

@lexer::members {
    def emit(self, token=None):
        # call the base class method
        Lexer.emit(self, token)
        # append token to stack
        self.token_stack.append(self._state.token)

    def nextToken(self):
        # call the base class method
        Lexer.nextToken(self)
        try:
            # pop token from stack
            return self.token_stack.pop(0)
        except IndexError:
            # pop from empty list raises index error
            # flag end of file
            return EOF_TOKEN
}

NEWLINE
@init {
    indent = 0
}
    :
        (
            (('\f')? ('\r')? '\n'
                {
                    self.emit(ClassicToken(NEWLINE, "\n"));
                }
            )
            |
            ' ')*
        (('\f')? ('\r')? '\n'
            {
                self.emit(ClassicToken(NEWLINE, "\n"));
            }
        )
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
                pass
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
    :   formatdef declarations EOF
    ;

formatdef
    :   longdoc FILEFORMAT FORMATNAME shortdoc
    ;

declarations
    :   typeblock? parameterblock? classblock*
    ;

// Short documentation following a definition, followed by one or more newlines.
// Because short style documentation always should come at the end of a definition,
// it includes the newline(s) that follow the definition (this makes the other parser
// rules a bit simpler).
shortdoc
    :   SHORTDOC? NEWLINE+
    ;

// Documentation preceeding a definition, with single newline following each line of text
// the number of lines in the documentation is arbitrary, also zero lines is possible (i.e.
// no documentation at all).
longdoc
    :   (SHORTDOC NEWLINE)*
    ;

typeblock
    :   TYPE blockbegin typedef+ blockend
    ;

parameterblock
    :   PARAMETER blockbegin fielddef+ blockend
    ;

classblock
    :   longdoc CLASS TYPENAME blockbegin declarations class_fielddefs blockend
    ;

blockbegin
    :   COLON NEWLINE INDENT
    ;

blockend
    :   DEDENT
    ;

typedef
    :   longdoc TYPENAME shortdoc // basic type
    |   longdoc TYPENAME '=' TYPENAME shortdoc // alias
    ;

fielddef
    :   longdoc TYPENAME VARIABLENAME fieldparameters? shortdoc
    ;

class_fielddefs_ifelifelse_fragment
    :
        IF expression blockbegin class_fielddefs blockend
        (ELIF expression blockbegin class_fielddefs blockend)*
        (ELSE blockbegin class_fielddefs blockend)?
    ;

class_fielddefs
    :   (class_fielddefs_ifelifelse_fragment | fielddef)+
    ;

kwarg
    :   VARIABLENAME '=' expression
    ;

fieldparameters
    :   '(' kwarg (',' kwarg)* ')'
    ;

// TODO: operators such as and, or, not, ...
expression
    :   VARIABLENAME
    |   INT
    |   FLOAT
    |   STRING
    |   '(' expression ')' // remove brackets
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
