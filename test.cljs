(ns learnnext.core
	(:require
		[om.next :as om :refer-macros [defui]]
		[om.next.protocols :as p]
		[om.dom :as dom]
		[pdf.core :refer [and* or* not*] :refer-macros [defpdf pdf]]
		[heh.core :as heh :refer-macros [html]]
		[dollar.bill :as $ :refer [$]]
		[learnnext.data :as data])
	(:use [cljs.pprint :only [pprint]]))
 
(enable-console-print!)
 
($/append ($ "head") 
	($ "<style>#chart{font-size:.7em; font-family:courier;} 
			.column{display:inline-block; width:150px; border-right:1px solid black; padding:.2em .5em; border-bottom:1px dotted silver;}</style>"))

thing.core

(ns rainbow.sexpress)

(quote [
( ( ( ( ))))
[[(((([[[]]]))))[[[] []]]]]
((((()))))
(((())))])

'([(((([[][{[(())] ({([])[]})}] ]))))])
'( ( ( ( ( ( ( ( ( ) ) ) ) ) ) ) ) 
'([([([([([([([([([( )])])])])])])])])])
'((((((()))))))
'[() (())  [ (([([()])]))]]
'(((( [[ [[ (( [ ( [ ()])]))]]]]))))[ [[[] ]]]

;asdfjhasdf






(def app-state (atom {
	:app/title "Main Sequence Stars"
	:stars (into {} 
		(map 
			(fn [[class rgb hex]] 
				{class {:class class :color/rgb rgb :color/hex hex}})
		data/stellar-colors))}))
  
(def stars? #{:stars})
(def rgb? #(re-find #"rgb$" (str %)))
 
 (comment 
(defn read [data k]
	(if-let [local (get  @(:state data) k)]
    {:value local}
    {:value :not-found})))


(defpdf read)

(pdf read [data k]
  (get @(:state data) k :not-found))

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

(def star (om/factory Star))

(defui Widget
	static om/IQueryParams
  (params [this]
    {:start 0 :end 5})
  static om/IQuery
  (query [this] '[:app/title (:stars {:start ?start :end ?end})])
	Object
	(render [this]
		(let [props (om/props this)
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
 