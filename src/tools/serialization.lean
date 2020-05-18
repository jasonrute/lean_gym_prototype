import data.buffer.parser
import init.data.unsigned

def join (sep : string) : list string → string
| [x]     := x
| []      := ""
| (x::xs) := x ++ sep ++ join xs

namespace expr

namespace representation

private def escapec : char → string
| '\"' := "\\\""
| '\t' := "\\t"
| '\n' := "\\n"
| '\\' := "\\\\"
| c    := string.singleton c

private def escape (s : string) : string :=
s.fold "" (λ s c, s ++ escapec c)

def wrap_in_parens (ss : list string) : string := "( " ++ (join " " ss) ++ " )"

meta def form_of_string (s : string) : string := "\"" ++ (escape s) ++ "\""

meta def form_of_nat (n : nat) : string := to_string n

meta def form_of_unsigned (n : unsigned) : string := to_string n

meta def form_of_name : name → string
| name.anonymous         := wrap_in_parens ["name.anonymous"]
| (name.mk_string s nm)  := wrap_in_parens ["name.mk_string", form_of_string s, form_of_name nm]
| (name.mk_numeral i nm) := wrap_in_parens ["name.mk_numeral", form_of_unsigned i, form_of_name nm]

meta def form_of_lvl : level → string
| level.zero         := wrap_in_parens ["level.zero"]
| (level.succ l)     := wrap_in_parens ["level.succ", form_of_lvl l]
| (level.max l1 l2)  := wrap_in_parens ["level.max", form_of_lvl l1, form_of_lvl l2]
| (level.imax l1 l2) := wrap_in_parens ["level.imax", form_of_lvl l1, form_of_lvl l2]
| (level.param nm)   := wrap_in_parens ["level.param", form_of_name nm]
| (level.mvar nm)    := wrap_in_parens ["level.mvar", form_of_name nm]

meta def form_of_lvl_list : list level → string
| []       := wrap_in_parens ["list.nil"]
| (h :: t) := wrap_in_parens ["list.cons", form_of_lvl h, form_of_lvl_list t]

meta def form_of_binder_info : binder_info → string
| binder_info.default             := wrap_in_parens ["binder_info.default"]
| binder_info.implicit            := wrap_in_parens ["binder_info.implicit"]
| binder_info.strict_implicit     := wrap_in_parens ["binder_info.strict_implicit"]
| binder_info.inst_implicit       := wrap_in_parens ["binder_info.inst_implicit"]
| other                           := wrap_in_parens ["<other>"]

meta def form_of_expr : expr → string
| (expr.var i)                     := wrap_in_parens ["expr.var", (format.to_string (to_fmt i) options.mk)]
| (expr.sort lvl)                  := wrap_in_parens ["expr.sort", form_of_lvl lvl]
| (expr.const nm lvls)             := wrap_in_parens ["expr.const", form_of_name nm, form_of_lvl_list lvls]
| (expr.mvar nm nm' tp)            := wrap_in_parens ["expr.mvar", form_of_name nm, form_of_name nm',form_of_expr tp]
| (expr.local_const nm ppnm bi tp) := wrap_in_parens ["expr.local_const", form_of_name nm, form_of_name ppnm, form_of_binder_info bi, form_of_expr tp]
| (expr.app f e)                   := wrap_in_parens ["expr.app", form_of_expr f, form_of_expr e]
| (expr.lam nm bi tp bod)          := wrap_in_parens ["expr.lam", form_of_name nm, form_of_binder_info bi, form_of_expr tp, form_of_expr bod]
| (expr.pi nm bi tp bod)           := wrap_in_parens ["expr.pi", form_of_name nm, form_of_binder_info bi, form_of_expr tp, form_of_expr bod]
| (expr.elet nm tp val bod)        := wrap_in_parens ["<expr.elet>"]
| (expr.macro mdf mlst)            := wrap_in_parens ["<expr.macro>"]

meta instance name_has_repr : has_repr name := {
  repr := form_of_name
}

meta instance level_has_repr : has_repr level := {
  repr := form_of_lvl
}

meta instance binder_info_has_repr : has_repr binder_info := {
  repr := form_of_binder_info
}

meta instance expr_has_repr : has_repr expr := {
  repr := form_of_expr
}

end representation

open parser

def Ws : parser unit :=
decorate_error "<whitespace>" $
many' $ one_of' " \t\x0d\n".to_list

def tok (s : string) := str s >> Ws

def StringChar : parser char :=
sat (λc, c ≠ '\"' ∧ c ≠ '\\' ∧ c.val > 0x1f)
 <|> (do str "\\",
         (str "t" >> return '\t') <|>
         (str "n" >> return '\n') <|>
         (str "\\" >> return '\\') <|>
         (str "\"" >> return '\"'))

def BasicString : parser string :=
str "\"" *> (many_char StringChar) <* str "\"" <* Ws

def String := BasicString

def Nat : parser nat :=
do s ← many_char1 (one_of "0123456789".to_list),
   Ws,
   return s.to_nat

def Unsigned : parser unsigned := unsigned.of_nat <$> Nat 

def Boolean : parser bool :=
(tok "true" >> return tt) <|>
(tok "false" >> return ff)


section name
parameter Name : parser name

def NameAnonymous : parser name := 
do
  tok "name.anonymous",
  return name.anonymous

def NameString : parser name := 
do
  tok "name.mk_string",
  s ← String,
  nm ← Name,
  return $ name.mk_string s nm

def NameNumeral : parser name := 
do
  tok "name.mk_numeral",
  i ← Unsigned,
  nm ← Name,
  return $ name.mk_numeral i nm

end name

def Name : parser name :=
fix $ λ Name, 
  let inner := NameAnonymous <|> (NameString Name) <|> (NameNumeral Name) in
  tok "(" *> inner <* tok ")"

section level
parameter Level : parser level

meta def LevelZero : parser level := 
do
do
  tok "level.zero",
  return level.zero

meta def LevelSucc : parser level := 
do
  tok "level.succ",
  l ← Level,
  return $ level.succ l

meta def LevelMax : parser level := 
do
  tok "level.max",
  l1 ← Level,
  l2 ← Level,
  return $ level.max l1 l2

meta def LevelIMax : parser level :=
do
  tok "level.imax",
  l1 ← Level,
  l2 ← Level,
  return $ level.imax l1 l2

meta def LevelParam : parser level :=
do
  tok "level.param",
  nm ← Name,
  return $ level.param nm

meta def LevelMVar : parser level :=
do
  tok "level.mvar",
  nm ← Name,
  return $ level.mvar nm

end level

meta def Level : parser level :=
fix $ λ Level, 
  let inner := LevelZero <|> LevelSucc Level <|> LevelMax Level <|> 
               LevelIMax Level <|> LevelParam <|> LevelMVar in
  tok "(" *> inner <* tok ")"

section list_level
parameter ListLevel : parser (list level)

meta def ListLevelNil : parser (list level) := 
do
  tok "list.nil",
  return list.nil

meta def ListLevelCons : parser (list level) :=
do
  tok "list.cons",
  h ← Level,
  t ← ListLevel,
  return $ list.cons h t

end list_level

meta def ListLevel : parser (list level) :=
fix $ λ ListLevel, 
  let inner := ListLevelNil <|> ListLevelCons ListLevel in
  tok "(" *> inner <* tok ")"


section binder_info
parameter BinderInfo : parser binder_info

def BinderInfoDefault : parser binder_info := 
do
  tok "binder_info.default",
  return binder_info.default

def BinderInfoImplicit : parser binder_info :=
do
  tok "binder_info.implicit",
  return binder_info.implicit

def BinderInfoStrictImplicit : parser binder_info :=
do
  tok "binder_info.strict_implicit",
  return binder_info.strict_implicit

def BinderInfoInstImplicit : parser binder_info :=
do
  tok "binder_info.inst_implicit",
  return binder_info.inst_implicit
  

end binder_info

def BinderInfo : parser binder_info :=
fix $ λ BinderInfo,
  let inner := BinderInfoDefault <|> BinderInfoImplicit <|> 
               BinderInfoStrictImplicit <|> BinderInfoInstImplicit in
  tok "(" *> inner <* tok ")"


section expr
parameter Expr : parser expr

--TODO: Fix the optional params in these

meta def ExprVar : parser expr :=
do
  tok "expr.var",
  i ← Nat,
  return $ expr.var i

meta def ExprSort : parser expr :=
do
  tok "expr.sort",
  lvl ← Level,
  return $ expr.sort lvl

meta def ExprConst : parser expr :=
do
  tok "expr.const",
  nm ← Name,
  lvls ← ListLevel,
  return $ expr.const nm lvls

meta def ExprMVar : parser expr :=
do
  tok "expr.mvar",
  nm1 ← Name,
  nm2 ← Name,
  tp ← Expr,
  return $ expr.mvar nm1 nm2 tp

meta def ExprLocalConst : parser expr :=
do
  tok "expr.local_const",
  nm ← Name,
  ppnm ← Name,
  bi ← BinderInfo,
  tp ← Expr,
  return $ expr.local_const nm ppnm bi tp

meta def ExprApp : parser expr :=
do
  tok "expr.app",
  f ← Expr,
  e ← Expr,
  return $ expr.app f e

meta def ExprLam : parser expr :=
do
  tok "expr.lam",
  nm ← Name,
  bi ← BinderInfo,
  tp ← Expr,
  bod ← Expr,
  return $ expr.lam nm bi tp bod

meta def ExprPi : parser expr :=
do
  tok "expr.pi",
  nm ← Name,
  bi ← BinderInfo,
  tp ← Expr,
  bod ← Expr,
  return $ expr.pi nm bi tp bod

end expr

meta def Expr : parser expr :=
fix $ λ Expr, 
  let inner := ExprVar <|> ExprSort <|> ExprConst <|> ExprMVar Expr <|> 
               ExprLocalConst Expr <|> ExprApp Expr <|> ExprLam Expr <|> ExprPi Expr in
  tok "(" *> inner <* tok ")"

meta def deserialize : string → string ⊕ expr := run_string Expr
meta def deserialize_name : string → string ⊕ name := run_string Name

/-
meta def get_right {α β : Type} (s: α ⊕ β) : β :=
match s with
| (sum.inl a) := sorry
| (sum.inr b) := b
end

#eval get_right $ run_string Name $ "( name.anonymous )"
#eval get_right $ run_string Name $ "( name.mk_string \"hello\" ( name.anonymous ) )"
#eval get_right $ run_string Name $ "( name.mk_numeral 145 ( name.anonymous ) )"

#eval get_right $ run_string ListLevel $ "( list.nil )"
#eval get_right $ run_string ListLevel $ "( list.cons ( level.zero ) ( list.nil ) )"

#eval get_right $ run_string Level $ "( level.zero )"
#eval get_right $ run_string Level $ "( level.succ ( level.zero ) )"
#eval get_right $ run_string Level $ "( level.max ( level.zero ) ( level.zero ) )"
#eval get_right $ run_string Level $ "( level.imax ( level.zero ) ( level.zero ) )"
#eval get_right $ run_string Level $ "( level.param ( name.anonymous ) )"
#eval get_right $ run_string Level $ "( level.mvar ( name.anonymous ) )"

#eval get_right $ run_string BinderInfo $ "( binder_info.default )"
#eval get_right $ run_string BinderInfo $ "( binder_info.implicit )"
#eval get_right $ run_string BinderInfo $ "( binder_info.strict_implicit )"
#eval get_right $ run_string BinderInfo $ "( binder_info.inst_implicit )"
#eval get_right $ run_string BinderInfo $ "( <other> )"

#eval get_right $ run_string Expr $ "( expr.var 145 )"
#eval get_right $ run_string Expr $ "( expr.sort ( level.zero ) )"
#eval get_right $ run_string Expr $ "( expr.const ( name.mk_string \"nat\" ( name.anonymous ) ) ( list.nil ) )"
#eval get_right $ run_string Expr $ "( expr.mvar ( name.mk_numeral 477 ( name.mk_numeral 2140 ( name.mk_string \"_fresh\" ( name.mk_string \"_mlocal\" ( name.anonymous ) ) ) ) ) ( name.mk_numeral 477 ( name.mk_numeral 2140 ( name.mk_string \"_fresh\" ( name.mk_string \"_mlocal\" ( name.anonymous ) ) ) ) ) ( expr.const ( name.mk_numeral 2 ( name.anonymous ) ) ( list.nil ) ) )"
#eval get_right $ run_string Expr $ "( expr.local_const ( name.mk_string \"hello\" ( name.anonymous ) ) ( name.mk_string \"hello\" ( name.anonymous ) ) ( binder_info.default ) ( expr.sort ( level.zero ) ) )"
#eval get_right $ run_string Expr $ "( expr.app ( expr.local_const ( name.mk_numeral 1319 ( name.mk_numeral 1092 ( name.mk_string \"_fresh\" ( name.mk_numeral 0 ( name.anonymous ) ) ) ) ) ( name.mk_string \"p\" ( name.anonymous ) ) ( binder_info.default ) ( expr.const ( name.mk_numeral 1 ( name.anonymous ) ) ( list.nil ) ) ) ( expr.local_const ( name.mk_numeral 1320 ( name.mk_numeral 1092 ( name.mk_string \"_fresh\" ( name.mk_numeral 0 ( name.anonymous ) ) ) ) ) ( name.mk_string \"n\" ( name.anonymous ) ) ( binder_info.default ) ( expr.const ( name.mk_numeral 1 ( name.anonymous ) ) ( list.nil ) ) ) )"
#eval get_right $ run_string Expr $ "( expr.lam ( name.mk_string \"n\" ( name.anonymous ) ) ( binder_info.default ) ( expr.const ( name.mk_string \"nat\" ( name.anonymous ) ) ( list.nil ) ) ( expr.app ( expr.local_const ( name.mk_numeral 939 ( name.mk_numeral 2261 ( name.mk_string \"_fresh\" ( name.mk_numeral 0 ( name.anonymous ) ) ) ) ) ( name.mk_string \"p\" ( name.anonymous ) ) ( binder_info.default ) ( expr.const ( name.mk_numeral 1 ( name.anonymous ) ) ( list.nil ) ) ) ( expr.var 0 ) ) )"
#eval get_right $ run_string Expr $ "( expr.pi ( name.mk_string \"a\" ( name.anonymous ) ) ( binder_info.default ) ( expr.const ( name.mk_string \"nat\" ( name.anonymous ) ) ( list.nil ) ) ( expr.sort ( level.zero ) ) )"

#eval get_right $ run_string Expr $ "( expr.app ( expr.app ( expr.app ( expr.const ( name.mk_string \"eq\" ( name.anonymous ) ) ( list.cons ( level.succ ( level.zero ) ) ( list.nil ) ) ) ( expr.pi ( name.mk_string \"a\" ( name.anonymous ) ) ( binder_info.default ) ( expr.const ( name.mk_string \"nat\" ( name.anonymous ) ) ( list.nil ) ) ( expr.sort ( level.zero ) ) ) ) ( expr.local_const ( name.mk_numeral 939 ( name.mk_numeral 2261 ( name.mk_string \"_fresh\" ( name.mk_numeral 0 ( name.anonymous ) ) ) ) ) ( name.mk_string \"p\" ( name.anonymous ) ) ( binder_info.default ) ( expr.const ( name.mk_numeral 1 ( name.anonymous ) ) ( list.nil ) ) ) ) ( expr.lam ( name.mk_string \"n\" ( name.anonymous ) ) ( binder_info.default ) ( expr.const ( name.mk_string \"nat\" ( name.anonymous ) ) ( list.nil ) ) ( expr.app ( expr.local_const ( name.mk_numeral 939 ( name.mk_numeral 2261 ( name.mk_string \"_fresh\" ( name.mk_numeral 0 ( name.anonymous ) ) ) ) ) ( name.mk_string \"p\" ( name.anonymous ) ) ( binder_info.default ) ( expr.const ( name.mk_numeral 1 ( name.anonymous ) ) ( list.nil ) ) ) ( expr.var 0 ) ) ) )"
#eval get_right $ run_string Expr $ "( expr.pi ( name.mk_string \"n\" ( name.anonymous ) ) ( binder_info.default ) ( expr.const ( name.mk_string \"nat\" ( name.anonymous ) ) ( list.nil ) ) ( expr.pi ( name.mk_string \"m\" ( name.anonymous ) ) ( binder_info.default ) ( expr.const ( name.mk_string \"nat\" ( name.anonymous ) ) ( list.nil ) ) ( expr.app ( expr.app ( expr.app ( expr.const ( name.mk_string \"eq\" ( name.anonymous ) ) ( list.cons ( level.succ ( level.zero ) ) ( list.nil ) ) ) ( expr.const ( name.mk_string \"nat\" ( name.anonymous ) ) ( list.nil ) ) ) ( expr.app ( expr.app ( expr.app ( expr.app ( expr.const ( name.mk_string \"add\" ( name.mk_string \"has_add\" ( name.anonymous ) ) ) ( list.cons ( level.zero ) ( list.nil ) ) ) ( expr.const ( name.mk_string \"nat\" ( name.anonymous ) ) ( list.nil ) ) ) ( expr.const ( name.mk_string \"has_add\" ( name.mk_string \"nat\" ( name.anonymous ) ) ) ( list.nil ) ) ) ( expr.var 1 ) ) ( expr.var 0 ) ) ) ( expr.app ( expr.app ( expr.app ( expr.app ( expr.const ( name.mk_string \"add\" ( name.mk_string \"has_add\" ( name.anonymous ) ) ) ( list.cons ( level.zero ) ( list.nil ) ) ) ( expr.const ( name.mk_string \"nat\" ( name.anonymous ) ) ( list.nil ) ) ) ( expr.const ( name.mk_string \"has_add\" ( name.mk_string \"nat\" ( name.anonymous ) ) ) ( list.nil ) ) ) ( expr.var 0 ) ) ( expr.var 1 ) ) ) ) )"
#eval get_right $ run_string Expr $ "( expr.local_const ( name.mk_numeral 1094 ( name.mk_numeral 2785 ( name.mk_string \"_fresh\" ( name.mk_numeral 0 ( name.anonymous ) ) ) ) ) ( name.mk_string \"n\" ( name.anonymous ) ) ( binder_info.default ) ( expr.const ( name.mk_numeral 1 ( name.anonymous ) ) ( list.nil ) ) )"
-/

end expr
