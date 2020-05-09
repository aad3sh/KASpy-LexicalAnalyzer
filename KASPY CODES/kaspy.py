import string

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

KEYWORDS=[
	'kINT',
	'kFLOAT'
]

class Position:
	def __init__(self, idx, ln, col, ftxt):
		self.idx = idx
		self.ln = ln
		self.col = col
		self.ftxt = ftxt

	def advance(self, current_char=None):
		self.idx += 1
		self.col += 1

		if current_char == '\n':
			self.ln += 1
			self.col = 0

		return self

	def copy(self):
		return Position(self.idx, self.ln, self.col,self.ftxt)

class Token:
	def __init__(self, type_, value=None, pos_start=None, pos_end=None):
		self.type = type_
		self.value = value

		if pos_start:
			self.pos_start = pos_start.copy()
			self.pos_end = pos_start.copy()
			self.pos_end.advance()

		if pos_end:
			self.pos_end = pos_end.copy()

	def matches(self, type_, value):
		return self.type == type_ and self.value == value
	
	def __repr__(self):
		if self.value: return f'{self.type}:{self.value}'
		return f'{self.type}'

class Lexer:
	def __init__(self,text):
		self.text = text
		self.pos = Position(-1, 0, -1, text)
		self.current_char = None
		self.advance()
	
	def advance(self):
		self.pos.advance(self.current_char)
		self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

	def make_tokens(self):
		tokens = []

		while self.current_char != None:
			if self.current_char in ' \t':
				self.advance()
			elif self.current_char in DIGITS:
				tokens.append(self.make_number())
			elif self.current_char in LETTERS:
				tokens.append(self.make_identifier())
			elif self.current_char == '+':
				tokens.append(Token('PLUS', pos_start=self.pos))
				self.advance()
			elif self.current_char == '-':
				tokens.append(Token('MINUS', pos_start=self.pos))
				self.advance()
			elif self.current_char == '*':
				tokens.append(Token('MULTIPLY', pos_start=self.pos))
				self.advance()
			elif self.current_char == '/':
				tokens.append(Token('DIVISION', pos_start=self.pos))
				self.advance()
			elif self.current_char == '^':
				tokens.append(Token('POWER', pos_start=self.pos))
				self.advance()
			elif self.current_char == '%':
				tokens.append(Token('MODULUS', pos_start=self.pos))
				self.advance()
			elif self.current_char == '=':
				tokens.append(Token('EQUALS', pos_start=self.pos))
				self.advance()
			elif self.current_char == '(':
				tokens.append(Token('LPAREN', pos_start=self.pos))
				self.advance()
			elif self.current_char == ')':
				tokens.append(Token('RPAREN', pos_start=self.pos))
				self.advance()
			else:
				pos_start = self.pos.copy()
				char = self.current_char
				self.advance()
				print("Token not generated")

		tokens.append(Token('EOF', pos_start=self.pos))
		return tokens, None

	def make_number(self):
		num_str = ''
		dot_count = 0
		pos_start = self.pos.copy()

		while self.current_char != None and self.current_char in DIGITS + '.':
			if self.current_char == '.':
				if dot_count == 1: break
				dot_count += 1
			num_str += self.current_char
			self.advance()

		global var_type
		if dot_count == 0:
			return Token('INT', int(num_str), pos_start, self.pos)
		else:
			if var_type==1:
				return Token('INT', int(float(num_str)), pos_start, self.pos)
			elif var_type==2 or var_type==3:
				return Token('FLOAT', float(num_str), pos_start, self.pos)

	def make_identifier(self):
		id_str = ''
		pos_start = self.pos.copy()

		while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
			id_str += self.current_char
			self.advance()

		tok_type = 'KEYWORD' if id_str in KEYWORDS else 'IDENTIFIER'
		return Token(tok_type, id_str, pos_start, self.pos)

class NumberNode:
	def __init__(self, tok):
		self.tok = tok

		self.pos_start = self.tok.pos_start
		self.pos_end = self.tok.pos_end

	def __repr__(self):
		return f'{self.tok}'

class kINTAccessNode:
	def __init__(self, kINT_name_tok):
		self.kINT_name_tok = kINT_name_tok

		self.pos_start = self.kINT_name_tok.pos_start
		self.pos_end = self.kINT_name_tok.pos_end

class kINTAssignNode:
	def __init__(self, kINT_name_tok, value_node):
		self.kINT_name_tok = kINT_name_tok
		self.value_node = value_node

		self.pos_start = self.kINT_name_tok.pos_start
		self.pos_end = self.value_node.pos_end

class BinOpNode:
	def __init__(self, left_node, op_tok, right_node):
		self.left_node = left_node
		self.op_tok = op_tok
		self.right_node = right_node

		self.pos_start = self.left_node.pos_start
		self.pos_end = self.right_node.pos_end

	def __repr__(self):
		return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
	def __init__(self, op_tok, node):
		self.op_tok = op_tok
		self.node = node

		self.pos_start = self.op_tok.pos_start
		self.pos_end = node.pos_end

	def __repr__(self):
		return f'({self.op_tok}, {self.node})'

class ParseResult:
	def __init__(self):
		self.error = None
		self.node = None
		self.advance_count = 0

	def register_advancement(self):
		self.advance_count += 1

	def register(self, res):
		self.advance_count += res.advance_count
		if res.error: self.error = res.error
		return res.node

	def success(self, node):
		self.node = node
		return self

	def failure(self, error):
		if not self.error or self.advance_count == 0:
			self.error = error
		return self

# PARSER
class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.tok_idx = -1
		self.advance()

	def advance(self, ):
		self.tok_idx += 1
		if self.tok_idx < len(self.tokens):
			self.current_tok = self.tokens[self.tok_idx]
		return self.current_tok

	def parse(self):
		res = self.expr()
		if not res.error and self.current_tok.type != 'EOF':
			print("Expected '+', '-', '*', '/' or '^'")
		return res

	def root(self):
		res = ParseResult()
		tok = self.current_tok

		if tok.type in ('INT', 'FLOAT'):
			res.register_advancement()
			self.advance()
			return res.success(NumberNode(tok))

		elif tok.type == 'IDENTIFIER':
			res.register_advancement()
			self.advance()
			return res.success(kINTAccessNode(tok))

		elif tok.type == 'LPAREN':
			res.register_advancement()
			self.advance()
			expr = res.register(self.expr())
			if res.error: return res
			if self.current_tok.type == 'RPAREN':
				res.register_advancement()
				self.advance()
				return res.success(expr)
			else:
				print("Expected ')'")

		print("Expected int, float, identifier, '+', '-' or '('")

	def power(self):
		return self.bin_op(self.root, ('POWER','MODULUS' ), self.factor)

	def factor(self):
		res = ParseResult()
		tok = self.current_tok

		if tok.type in ('PLUS', 'MINUS'):
			res.register_advancement()
			self.advance()
			factor = res.register(self.factor())
			if res.error: return res
			return res.success(UnaryOpNode(tok, factor))

		return self.power()

	def term(self):
		return self.bin_op(self.factor, ('MULTIPLY', 'DIVISION'))

	def expr(self):
		res = ParseResult()

		if self.current_tok.matches('KEYWORD', 'kINT') or self.current_tok.matches('KEYWORD','kFLOAT'):
			res.register_advancement()
			self.advance()

			if self.current_tok.type != 'IDENTIFIER':
				print("Expected identifier")

			kINT_name = self.current_tok
			res.register_advancement()
			self.advance()

			if self.current_tok.type != 'EQUALS':
				print("Expected '='")

			res.register_advancement()
			self.advance()
			expr = res.register(self.expr())
			if res.error: return res
			return res.success(kINTAssignNode(kINT_name, expr))

		node = res.register(self.bin_op(self.term, ('PLUS', 'MINUS')))

		if res.error:
			print("Expected 'kINT','kFLOAT' int, float, identifier, '+', '-' or '('")

		return res.success(node)

	def bin_op(self, func_a, ops, func_b=None):
		if func_b == None:
			func_b = func_a
		
		res = ParseResult()
		left = res.register(func_a())
		if res.error: return res

		while self.current_tok.type in ops:
			op_tok = self.current_tok
			res.register_advancement()
			self.advance()
			right = res.register(func_b())
			if res.error: return res
			left = BinOpNode(left, op_tok, right)

		return res.success(left)

class RTResult:
	def __init__(self):
		self.value = None
		self.error = None

	def register(self, res):
		if res.error: self.error = res.error
		return res.value

	def success(self, value):
		self.value = value
		return self

	def failure(self, error):
		self.error = error
		return self

class Number:
	def __init__(self, value):
		self.value = value
		self.set_pos()
		self.set_context()

	def set_pos(self, pos_start=None, pos_end=None):
		self.pos_start = pos_start
		self.pos_end = pos_end
		return self

	def set_context(self, context=None):
		self.context = context
		return self

	def add_to(self, other):
		if isinstance(other, Number):
			global var_type
			if var_type==1 or var_type==3:
				return Number(int(self.value + other.value)).set_context(self.context), None
			elif var_type==2:
				return Number(float(self.value + other.value)).set_context(self.context), None

	def sub_from(self, other):
		if isinstance(other, Number):
			if var_type==1 or var_type==3:
				return Number(int(self.value - other.value)).set_context(self.context), None
			elif var_type==2:
				return Number(float(self.value - other.value)).set_context(self.context), None

	def mul_by(self, other):
		if isinstance(other, Number):
			if var_type==1 or var_type==3:
				return Number(int(self.value * other.value)).set_context(self.context), None
			elif var_type==2:
				return Number(float(self.value * other.value)).set_context(self.context), None

	def div_by(self, other):
		if isinstance(other, Number):
			if other.value == 0:
				return None, RTError(
					other.pos_start, other.pos_end,
					'Division by zero',
					self.context
				)

			if var_type==1 or var_type==3:
				return Number(int(self.value / other.value)).set_context(self.context), None
			elif var_type==2:
				return Number(float(self.value / other.value)).set_context(self.context), None

	def raised_to(self, other):
		if isinstance(other, Number):
			if var_type==1 or var_type==3:
				return Number(int(self.value**other.value)).set_context(self.context), None
			elif var_type==2:
				return Number(float(self.value**other.value)).set_context(self.context), None

	def mod_of(self,other):
		if isinstance(other,Number):
			return Number(self.value%other.value).set_context(self.context),None

	def copy(self):
		copy = Number(self.value)
		copy.set_pos(self.pos_start, self.pos_end)
		copy.set_context(self.context)
		return copy
	
	def __repr__(self):
		return str(self.value)

class Context:
	def __init__(self, display_name, parent=None, parent_entry_pos=None):
		self.display_name = display_name
		self.parent = parent
		self.parent_entry_pos = parent_entry_pos
		self.symbol_table = None

class SymbolTable:
	def __init__(self):
		self.symbols = {}
		self.parent = None

	def get(self, name):
		value = self.symbols.get(name, None)
		if value == None and self.parent:
			return self.parent.get(name)
		return value

	def set(self, name, value):
		self.symbols[name] = value

	def remove(self, name):
		del self.symbols[name]

class Interpreter:
	def visit(self, node, context):
		method_name = f'visit_{type(node).__name__}'
		method = getattr(self, method_name, self.no_visit_method)
		return method(node, context)

	def no_visit_method(self, node, context):
		raise Exception(f'No visit_{type(node).__name__} method defined')

	def visit_NumberNode(self, node, context):
		return RTResult().success(
			Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
		)

	def visit_kINTAccessNode(self, node, context):
		res = RTResult()
		kINT_name = node.kINT_name_tok.value
		value = context.symbol_table.get(kINT_name)

		if not value:
			print(f"'{kINT_name}' is not defined",
				context)

		value = value.copy().set_pos(node.pos_start, node.pos_end)
		return res.success(value)

	def visit_kINTAssignNode(self, node, context):
		res = RTResult()
		kINT_name = node.kINT_name_tok.value
		value = res.register(self.visit(node.value_node, context))
		if res.error: return res

		context.symbol_table.set(kINT_name, value)
		return res.success(value)

	def visit_BinOpNode(self, node, context):
		res = RTResult()
		left = res.register(self.visit(node.left_node, context))
		if res.error: return res
		right = res.register(self.visit(node.right_node, context))
		if res.error: return res

		if node.op_tok.type == 'PLUS':
			result, error = left.add_to(right)
		elif node.op_tok.type == 'MINUS':
			result, error = left.sub_from(right)
		elif node.op_tok.type == 'MULTIPLY':
			result, error = left.mul_by(right)
		elif node.op_tok.type == 'DIVISION':
			result, error = left.div_by(right)
		elif node.op_tok.type == 'POWER':
			result, error = left.raised_to(right)
		elif node.op_tok.type == 'MODULUS':
			result, error = left.mod_of(right)

		if error:
			return res.failure(error)
		else:
			return res.success(result.set_pos(node.pos_start, node.pos_end))

	def visit_UnaryOpNode(self, node, context):
		res = RTResult()
		number = res.register(self.visit(node.node, context))
		if res.error: return res

		error = None

		if node.op_tok.type == 'MINUS':
			number, error = number.mul_by(Number(-1))

		if error:
			return res.failure(error)
		else:
			return res.success(number.set_pos(node.pos_start, node.pos_end))

global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number(0))


def run(text):
	global var_type
	if 'kINT' in text: 
		var_type=1
	elif 'kFLOAT' in text:
		var_type=2
	else:
		var_type=3
	increment=[]
	for i in text:
		increment.append(i)
	i=0
	if increment.count("+")==2 or increment.count("-")==2:
		while(i<len(text)-1):
			if(text[i]+text[i+1]=="++" or text[i]+text[i+1]=="--" ):
				if (i+2==len(text)) or (text[i+2]=='\t'):
					text=text[:i-1]+'('+text[i-1:i+1]+"1)"+text[i+2:]
				i=i+1
			else:
				i=i+1
	lexer = Lexer(text)
	tokens, error = lexer.make_tokens()
	if error: return None, error
	parser = Parser(tokens)
	ast = parser.parse()
	if ast.error: return None, ast.error
	interpreter = Interpreter()
	context = Context('<program>')
	context.symbol_table = global_symbol_table
	print(tokens)
	result = interpreter.visit(ast.node, context)
	return result.value, result.error