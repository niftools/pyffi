grammar FFI;

tokens {
	// emitted when indentation increases
	// see NEWLINE for details
	INDENT;
	// emitted when indentation decreases
	// see NEWLINE for details
	DEDENT;
}

@lexer::members {
	// current indentation level
	int current_indent = 0;
}

/*------------------------------------------------------------------
 * PARSER RULES
 *------------------------------------------------------------------*/

ffi
	:	formatdef typeblock?
	;

formatdef
	:	'fileformat' FORMATNAME NEWLINE
	;

typeblock
	:	'type' COLON INDENT (typedef NEWLINE)* typedef DEDENT
	;

typedef
	:	TYPENAME // basic type
	|	TYPENAME '=' TYPENAME // alias
	;

/*------------------------------------------------------------------
 * LEXER RULES
 *------------------------------------------------------------------*/

// whitespace and comments


COMMENT
    :   '#' ~('\n')* '\n' {$channel=HIDDEN;}
    ;

fragment
DIGIT	:	'0'..'9'
	;

fragment
DIGITS	:	DIGIT+
	;

INT
	// hex
	:	'0x' ( '0' .. '9' | 'a' .. 'f' | 'A' .. 'F' )+
	// octal
	|	'0o' ( '0' .. '7')+
	// binary
	|	'0b' ( '0' .. '1')+
	// decimal
	|	DIGITS+
	;

fragment
EXPONENT
	:    'e' ( '+' | '-' )? DIGITS
	;

FLOAT
	:	DIGITS '.' DIGITS EXPONENT?
	;

COLON
	:	':'
	;

fragment
LCLETTER:	'a'..'z'
	;

fragment
UCLETTER:	'A'..'Z'
	;

// UPPERCASE for format name

FORMATNAME
	:	UCLETTER (UCLETTER | DIGITS)*
	;

// lower_case_with_underscores for attribute names
ATTRIBUTENAME
	:	LCLETTER (LCLETTER | DIGITS | '_')*
	;

// CamelCase for type names
TYPENAME
	:	UCLETTER (LCLETTER | UCLETTER | DIGITS)*
	;

STRING
	:	'"' (ESC|~('\\'|'\n'|'"'))* '"'
	;

fragment
ESC
	:	'\\' .
	;

// newline followed by whitespace will emit extra INDENT and DEDENT tokens
NEWLINE
@init {
	int indent = 0;
}
	:	// ignore whitespace at end of line, lines that only consist of whitespace
		((('\f')? ('\r')? '\n') | ' ')*
		// but we need of course at least one real newline
		(('\f')? ('\r')? '\n')
		// eat indentation, and count it
		('    '  { indent++; } )*
        	{
        		// indentation increased by one level: emit INDENT
			if (indent == current_indent + 1) {
				current_indent++;
				emit(new ClassicToken(INDENT, ">"));
			}
			// indentation remained the same: emit NEWLINE
			else if (indent == current_indent) {
				emit(new ClassicToken(NEWLINE, "\n"));
			}
			// indentation decreased (by any level): emit DEDENT as many as there are levels
			else if (indent < current_indent) {
				while (indent < current_indent) {
					current_indent--;
					emit(new ClassicToken(DEDENT, "<"));
				}
			}
			// else: raise error
		}
	;

// ignore whitespace
WS
	: (' ')+ { $channel=HIDDEN; }
	;

