import os

def patch_app_jsx():
    app_path = os.path.join(os.path.dirname(__file__), "..", "..", "Frontend", "frontend 2", "src", "App.jsx")
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # 1. Update App component to hold state
    app_decl = "export default function App() {\n    const [screen,\n    setScreen]=useState(0);"
    new_app_decl = """export default function App() {
    const [screen, setScreen] = useState(0);
    const [apiResult, setApiResult] = useState(null);"""
    content = content.replace(app_decl, new_app_decl)
    
    # 2. Pass props
    cap_screen = "<CaptureScreen onNext="
    new_cap_screen = "<CaptureScreen setApiResult={setApiResult} onNext="
    content = content.replace(cap_screen, new_cap_screen)
    
    res_screen = "<ResultScreen onNext="
    new_res_screen = "<ResultScreen apiResult={apiResult} onNext="
    content = content.replace(res_screen, new_res_screen)
    
    # 3. Rewrite CaptureScreen declaration and logic
    old_cap_func = """function CaptureScreen({
    onNext, onBack

}) {
    const [state,
    setState]=useState("scanning"); // scanning | detected | captured
    const [flashOn,
    setFlashOn]=useState(false);
    const [msg,
    setMsg]=useState("Align your gold item in the ring");

    useEffect(()=> {
            const t1=setTimeout(()=> {
                    setState("detected"); setMsg("Object detected — hold steady…");
                }

                , 2500);

            const t2=setTimeout(()=> {
                    setFlashOn(true); setState("captured"); setMsg("✓ Image captured — analyzing…");
                }

                , 4500);

            const t3=setTimeout(()=> {
                    setFlashOn(false); onNext();
                }

                , 5500);

            return ()=> {
                clearTimeout(t1); clearTimeout(t2); clearTimeout(t3);
            }

            ;
        }

        , []);"""
        
    new_cap_func = """function CaptureScreen({ onNext, onBack, setApiResult }) {
    const [state, setState] = useState("scanning");
    const [flashOn, setFlashOn] = useState(false);
    const [msg, setMsg] = useState("Tap the ring to open camera & scan gold");
    const fileRef = useRef(null);

    const handleFile = async (e) => {
        const file = e.target.files[0];
        if(!file) return;
        setState("detected");
        setMsg("Image selected. AI Analysis running...");
        setFlashOn(true);
        setTimeout(() => setFlashOn(false), 200);

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch("http://127.0.0.1:8000/analyze", {
                method: "POST",
                body: formData
            });
            const data = await res.json();
            setApiResult(data);
            setState("captured");
            setMsg("✓ TrueKarat AI Analysis Complete!");
            setTimeout(onNext, 1200);
        } catch (err) {
            setMsg("Network Error. Ensure FastAPI is running.");
            setState("scanning");
        }
    };"""
    content = content.replace(old_cap_func, new_cap_func)
    
    # Add input file to CaptureScreen JSX
    old_scan_ring = """<div className= {
            `scan-ring $ {
                state==="detected" ? "detected" : ""
            }

            `
        }

        >"""
        
    new_scan_ring = """<input type="file" accept="image/*" capture="environment" ref={fileRef} style={{display:'none'}} onChange={handleFile} />
        <div onClick={() => fileRef.current?.click()} style={{cursor: 'pointer'}} className={`scan-ring ${state==="detected" ? "detected" : ""}`}>"""
    content = content.replace(old_scan_ring, new_scan_ring)
    
    # 4. Rewrite ResultScreen
    old_res_func = """function ResultScreen({
    onNext, onBack

}) {"""
    new_res_func = """function ResultScreen({ onNext, onBack, apiResult }) {"""
    content = content.replace(old_res_func, new_res_func)
    
    # Replace Verdict Banner
    old_verdict = """>PRE-APPROVED</div> <div style="""
    new_verdict = """>{apiResult?.verdict || "PRE-APPROVED"}</div> <div style="""
    content = content.replace(old_verdict, new_verdict)
    
    # Replace CountUp logic
    old_count = """<CountUp end= {
                    38000
                }

                prefix="₹" duration= {
                    1200
                }

                /> – <CountUp end= {
                    49000
                }"""
    new_count = """<CountUp end={apiResult?.min_value || 38000} prefix="₹" duration={1200} /> – <CountUp end={apiResult?.max_value || 49000}"""
    content = content.replace(old_count, new_count)
    
    # Replace Purity / Weight Grid
    old_grid = """[ ["Purity Band", "20K – 22K", GOLD],
                    ["Weight Range", "8.2g – 10.5g", "#F0EDE4"],
                    ["Genuineness", "84 / 100", TEAL],
                    ["Spoofing Risk", "LOW", "#22C55E"],
                    ["Confidence", "HIGH", "#22C55E"],
                    ]"""
    new_grid = """[ ["Jewelry Type", apiResult?.type || "Chain / Necklace", GOLD],
                    ["Purity Band", apiResult?.purity || "22K", GOLD],
                    ["Est. Weight", apiResult?.weight || "10.0g", "#F0EDE4"],
                    ["Genuineness", (apiResult?.trustScore || 84) + " / 100", TEAL],
                    ["Spoofing Risk", "LOW", "#22C55E"],
                    ]"""
    content = content.replace(old_grid, new_grid)
    
    # Replace TrustScore Gauge
    old_gauge = """<TrustGauge score= {
                    84
                }"""
    new_gauge = """<TrustGauge score={apiResult?.trustScore || 84}"""
    content = content.replace(old_gauge, new_gauge)
    
    # Replace Loan Eligible Text
    old_loan_text = """>₹32, 300–<br />₹41, 650</div>"""
    new_loan_text = """>{apiResult ? `₹${apiResult.min_value}` : "₹32,300"}</div>"""
    content = content.replace(old_loan_text, new_loan_text)
    
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print("Frontend App.jsx patched successfully!")

if __name__ == "__main__":
    patch_app_jsx()
