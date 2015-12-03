
(farts) foo 
(thing)  foo

 '[foo `(bar )]asdf [foo ]

#_ 
  (ns learnnext.core
	(:require
		[om.next :as om :refer-macros [defui]]
		[om.next.protocols :as p]
		[om.dom :as dom]
		[pdf.core :refer [and* or* not*] :refer-macros [defpdf pdf]]
		[heh.core :as heh :refer-macros [html]]
		[dollar.bill :as $ :refer [$]]
		[learnnext.data :as data])

	(:use [cljs.pprint :only [pprint]])) (foo) sdf 

lsdfk.cheese/*foo*
   cat
foo
foo.core/*baz*

*foo*
*
@(enable-console-print!)
 thing.core/asdlfkj
($/append ($ "head") 
	($ "<style>#chart{font-size:.7em; font-family:courier;} 
			.column{display:inline-block; width:150px; border-right:1px solid black; padding:.2em .5em; border-bottom:1px dotted silver;}</style>"))
@sdgf '(@( 'foo)) asfg sdf
dfg
'(ts.core/foo (:sldjf 37 )) asdf

@( '( @(+ 1 '(* 3 1) ) ))



(ns rainbow.sexpress)
(((((())))))
(quote [
( ( ( ( ))))
[[(((([[[]]]))))[[[] []]]]]
((((()))))
(((())))])

'([(((([[][{[(())] ({([])[]})}] ]))))] )

'(( ( ( ( ( ( ( @(+ 1 1) ) ) ) ) ) ) ) ) () ()

'([([([([([([([([([( )])])])])])])])])])

'((((((()))))))
'[() (())  [ (([([()])]))]]
'(((( [[ [[ (( [ ( [ ()])]))]]]]))))[ [[[] ]]]

fo.bazo/core

(def app-state (atom {
	:app/title "Main Sequence Stars"
	:stars (into {} 
		(map 
			(fn [[class rgb hex]] 
				{class {:class class :color/rgb rgb :color/hex hex}})
		data/stellar-colors))}))
  
(def stars? #{:stars})
(def rgb? #(re-find #"rgb$" (str %)))
(comment [ asdf] )
 (comment foo (sdlfkj))

(comment 
(defn read [data k] ;hello world
	(if-let [local (get (:state data) k) ]
    {:value local}
    {:value :not-found})))
*fart* 
@atom 
(defpdf read)
*fart*
(pdf read [data k]
  (get @(:state data) k :not-found ) )

(pdf read [data k _]
	(get @(:state data) k :not-found))

(pdf read [data k props]
  {props (and* :start :end)}
     (let [local (get  @(:state data) k)
        {:keys [start end]} props]
    {:value (take (- end start) (drop start local))}))

(pdf read [data k _]
	{k #{:app/title}}
	{:value (reverse (get @(:state data) k))})


(defn mutate [_ _ _] {})


(defui Star
  static om/IQuery
  (query [this] '[:class :color/rgb :color/hex])
	Object
	(render [this]
		(let [props (om/props this)]
			(html
				(<div.star 
					(<span.class.column (:class props))
					(<span.rgb.column 
						(style {:background (:color/hex props)})
						(str "rgb" (into '() (:color/rgb props))))
					(<span.class.column 
						(style {:background (:color/hex props)})
						(:color/hex props)) )))))
[[[[[[[]]]]]]]

;TODO
; [x] #_ ignore pair
; [ ] fix newlines breaking basic forms
; [x] hashmap capture
;     [ ] sexpr pairs
; [x] special form scoping
; [x] illegalize nested lambdas, naked lambda args
; [x] scope for clojure.core fns

; [ ] gensym foo#



#_ rainbows
((((((((((((()))))))))))))
[({[({[({[({[]})]})]})]})]

#_ symbols
methods userland foo.core/qualified

#_ literals
12 2.9 3/6 0xBADA55 9r8012 07123 -1.2e-5 4.2M 18N 
:keyword ::qualified :foo.core/resolved
"Jane's sign said \"welcome\""
#<GameObject Foo (UnityEngine.GameObject)>

#_ specials
@(atomic) @foo
'( #(re-find #"rgb$\(" (str %3)))

'(reader [quoted @(form)])

#_ macro-specials
(defmacro fun [sym args & code] 
  `(do
      (prn ~[sym args])
      (comment (def ~'foo 7))
      (def ~sym [~'a b] 
        ~@code)))

;TODO illegalize
[foo/ /baz  %1 ::foo.bar/quaz .67 #(#()) {1 2 3}]
;TODO legalize
[:./d :. :./. ]

;TODO scope
[clojure.pprint/*thing* #'foo foo#
 #?(:cljs reader-conditional) ^{:meta 'form }]

;TODO fix-sexpr
[ {'foo}]

;TODO why is this recursing? - qualified_symbol: to blame
;form-init3272591183026652226.clj



(def subscript 
  {0 '₀ 1 '₁ 2 '₂ 3 '₃ 4 '₄ 5 '₅ 6 '₆ 7 '₇ 8 '₈ 9 '₉ '+ '₊ '- '₋ '= '₌ :open '₍ :close '₎})

(defn sub-int [n] 
  (symbol (apply str 
    (concat 
      (if (neg? n) ['₋] []) 
      (mapv (comp 
        #(get subscript % '?) 
        int 
        str) 
      (seq (str (int n))))))))

(defn sub-list [s] 
  (symbol (apply str (concat ['₍] [s] ['₎]))))
#_
(defn baz [a b c]
  (map 
    (comp ;ridic
      #(re-find #"rgb$\(" (str %))
      #(* % %)) 
    (get {:foo.core/thing [1 2/7 3 4.6]}
      ::thing)))








fii

[dfjk]






clojure.string/lowercase

(comment) 
#_  asdf adf 

gii
#_ (defui Widget
	static om/IQueryParams
  (params [this]
    {:start 0 :end 5})
  static om/IQuery
  (query [this] '[:app/title (:stars {:start ?start :end ?end})])
	Object
	(render [this]
		(comment )(let [props (om/props this)
				  stars (:stars props)]
			(html
				(<h1#title (:app/title props) ) (<hr)
        (map 
          (fn [[k v]]
            (<label (clj->js k) 
            (<input 
              (value (str v))
              (onChange (fn [e] 
                (om/set-params! this 
                  (conj (om/params this) 
                    {k (int (.. e -target -value))}))
                (prn (om/params this)))))))
          (om/params this))
				(<div#chart
					(map #(<span.column %) (clj->js (keys (last (last stars)))))
					(map #(star (assoc (last %) :om-index (gensym))) stars)))))) 
  
 
 

(def reconciler (om/reconciler {:state app-state :parser (om/parser {:read read :mutate mutate})}))

(om/add-root! reconciler Widget (first ($ "#app")))
 