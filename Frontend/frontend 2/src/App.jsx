import {
    useState,
    useEffect,
    useRef,
    useCallback
}

from "react";

const GOLD="#C9A84C";
const GOLD_LIGHT="#E8C96A";
const GOLD_DIM="#8B6914";
const NAVY="#0A0E1A";
const NAVY2="#0D1526";
const NAVY3="#111D35";
const BLUE_GLOW="#1E4ED8";
const TEAL="#0ECFCF";

const css=` @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    -webkit-tap-highlight-color: transparent;
}

.tk-app {
    font-family: 'DM Sans', sans-serif;

    background: $ {
        NAVY
    }

    ;
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 1rem;
    overflow: hidden;
}

.phone-frame {
    width: 375px;
    height: 812px;

    background: $ {
        NAVY2
    }

    ;
    border-radius: 44px;
    overflow: hidden;
    position: relative;
    box-shadow: 0 0 0 1px rgba(201, 168, 76, 0.15),
    0 0 80px rgba(30, 78, 216, 0.2),
    0 40px 80px rgba(0, 0, 0, 0.8);
}

.screen {
    position: absolute;
    inset: 0;
    overflow-y: auto;
    overflow-x: hidden;
    scrollbar-width: none;
    transition: transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.4s ease;
}

.screen::-webkit-scrollbar {
    display: none;
}

.screen.enter {
    transform: translateX(0) scale(1);
    opacity: 1;
}

.screen.exit-left {
    transform: translateX(-110%) scale(0.95);
    opacity: 0;
    pointer-events: none;
}

.screen.exit-right {
    transform: translateX(110%) scale(0.95);
    opacity: 0;
    pointer-events: none;
}

.screen.from-right {
    transform: translateX(110%) scale(0.95);
    opacity: 0;
    pointer-events: none;
}

.screen.from-left {
    transform: translateX(-110%) scale(0.95);
    opacity: 0;
    pointer-events: none;
}

.bg-deep {
    background: linear-gradient(160deg, #0A0E1A 0%, #0D1526 40%, #0A1020 100%);
}

.gold-text {
    color: $ {
        GOLD
    }

    ;
}

.white-text {
    color: #F0EDE4;
}

.muted-text {
    color: rgba(240, 237, 228, 0.5);
}

.teal-text {
    color: $ {
        TEAL
    }

    ;
}

.tk-btn-primary {
    background: linear-gradient(135deg, $ {
            GOLD
        }

        0%, #A87D28 100%);
    color: #0A0E1A;
    border: none;
    border-radius: 16px;
    font-family: 'Syne',
    sans-serif;
    font-weight: 700;
    font-size: 15px;
    padding: 16px 32px;
    cursor: pointer;
    width: 100%;
    letter-spacing: 0.03em;
    position: relative;
    overflow: hidden;
    transition: transform 0.15s ease,
    box-shadow 0.15s ease;
}

.tk-btn-primary:active {
    transform: scale(0.96);
}

.tk-btn-primary::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, transparent 60%);
    border-radius: inherit;
}

.tk-btn-ghost {
    background: rgba(201, 168, 76, 0.08);

    color: $ {
        GOLD
    }

    ;
    border: 1px solid rgba(201, 168, 76, 0.25);
    border-radius: 16px;
    font-family: 'DM Sans',
    sans-serif;
    font-weight: 500;
    font-size: 14px;
    padding: 14px 28px;
    cursor: pointer;
    width: 100%;
    transition: transform 0.15s ease,
    background 0.2s ease;
}

.tk-btn-ghost:active {
    transform: scale(0.96);
    background: rgba(201, 168, 76, 0.12);
}

.glass-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    backdrop-filter: blur(12px);
}

.glow-card {
    background: linear-gradient(135deg, rgba(30, 78, 216, 0.12) 0%, rgba(14, 207, 207, 0.06) 100%);
    border: 1px solid rgba(201, 168, 76, 0.15);
    border-radius: 20px;
}

.step-bar {
    display: flex;
    gap: 6px;
    padding: 0 24px;
    margin-bottom: 8px;
}

.step-dot {
    height: 3px;
    border-radius: 2px;
    background: rgba(201, 168, 76, 0.2);
    flex: 1;
    transition: background 0.3s ease;
}

.step-dot.active {
    background: $ {
        GOLD
    }

    ;
}

.step-dot.done {
    background: rgba(201, 168, 76, 0.5);
}

.otp-box {
    width: 52px;
    height: 60px;
    background: rgba(255, 255, 255, 0.05);
    border: 1.5px solid rgba(201, 168, 76, 0.2);
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Syne', sans-serif;
    font-size: 24px;
    font-weight: 700;

    color: $ {
        GOLD
    }

    ;
    transition: border-color 0.3s ease,
    transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.otp-box.filled {
    border-color: $ {
        GOLD
    }

    ;
    background: rgba(201, 168, 76, 0.08);
    transform: scale(1.05);
}

.otp-box.success {
    border-color: #22C55E;
    background: rgba(34, 197, 94, 0.1);
    transform: scale(1.08);
}

.camera-overlay {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
}

.scan-ring {
    width: 220px;
    height: 220px;
    border-radius: 50%;
    border: 2px solid rgba(201, 168, 76, 0.4);
    position: relative;
    animation: ringPulse 2s ease-in-out infinite;
}

@keyframes ringPulse {

    0%,
    100% {
        transform: scale(1);
        border-color: rgba(201, 168, 76, 0.4);
        box-shadow: 0 0 0 0 rgba(201, 168, 76, 0.1);
    }

    50% {
        transform: scale(1.03);
        border-color: rgba(201, 168, 76, 0.7);
        box-shadow: 0 0 40px rgba(201, 168, 76, 0.15);
    }
}

.scan-ring.detected {
    border-color: rgba(14, 207, 207, 0.8);
    box-shadow: 0 0 40px rgba(14, 207, 207, 0.25);
    animation: detectedPulse 1s ease-in-out infinite;
}

@keyframes detectedPulse {

    0%,
    100% {
        box-shadow: 0 0 20px rgba(14, 207, 207, 0.2);
    }

    50% {
        box-shadow: 0 0 60px rgba(14, 207, 207, 0.4);
    }
}

.corner-tl,
.corner-tr,
.corner-bl,
.corner-br {
    position: absolute;
    width: 24px;
    height: 24px;
}

.corner-tl {
    top: -1px;
    left: -1px;

    border-top: 2px solid $ {
        GOLD
    }

    ;

    border-left: 2px solid $ {
        GOLD
    }

    ;
    border-radius: 6px 0 0 0;
}

.corner-tr {
    top: -1px;
    right: -1px;

    border-top: 2px solid $ {
        GOLD
    }

    ;

    border-right: 2px solid $ {
        GOLD
    }

    ;
    border-radius: 0 6px 0 0;
}

.corner-bl {
    bottom: -1px;
    left: -1px;

    border-bottom: 2px solid $ {
        GOLD
    }

    ;

    border-left: 2px solid $ {
        GOLD
    }

    ;
    border-radius: 0 0 0 6px;
}

.corner-br {
    bottom: -1px;
    right: -1px;

    border-bottom: 2px solid $ {
        GOLD
    }

    ;

    border-right: 2px solid $ {
        GOLD
    }

    ;
    border-radius: 0 0 6px 0;
}

.waveform-bar {
    width: 4px;
    border-radius: 4px;

    background: linear-gradient(to top, $ {
            GOLD_DIM
        }

        , $ {
            GOLD_LIGHT
        });
    transform-origin: bottom;
    transition: height 0.08s ease;
}

.analysis-step {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    opacity: 0;
    transform: translateY(10px);
    transition: opacity 0.4s ease, transform 0.4s ease;
}

.analysis-step.visible {
    opacity: 1;
    transform: translateY(0);
}

.step-icon-ring {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: 1.5px solid rgba(201, 168, 76, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    font-size: 14px;
    transition: all 0.3s ease;
}

.step-icon-ring.done {
    border-color: #22C55E;
    background: rgba(34, 197, 94, 0.1);
}

.step-icon-ring.active {
    border-color: $ {
        GOLD
    }

    ;
    background: rgba(201, 168, 76, 0.1);
    box-shadow: 0 0 12px rgba(201, 168, 76, 0.2);
}

.count-up {
    font-family: 'Syne', sans-serif;
    font-weight: 800;

    color: $ {
        GOLD
    }

    ;
}

.trust-gauge {
    position: relative;
    width: 120px;
    height: 60px;
    overflow: hidden;
}

.result-value-card {
    background: linear-gradient(135deg, rgba(201, 168, 76, 0.08) 0%, rgba(30, 78, 216, 0.06) 100%);
    border: 1px solid rgba(201, 168, 76, 0.15);
    border-radius: 16px;
    padding: 14px 16px;
}

.verdict-banner {
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.12) 0%, rgba(34, 197, 94, 0.06) 100%);
    border: 1px solid rgba(34, 197, 94, 0.3);
    border-radius: 18px;
    padding: 18px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    position: relative;
    overflow: hidden;
}

.shimmer {
    position: relative;
    overflow: hidden;
}

.shimmer::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 60%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(201, 168, 76, 0.15), transparent);
    animation: shimmer 2.5s ease infinite;
}

@keyframes shimmer {
    0% {
        left: -60%;
    }

    100% {
        left: 140%;
    }
}

.tk-input {
    width: 100%;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(201, 168, 76, 0.2);
    border-radius: 14px;
    padding: 16px 18px;
    font-family: 'DM Sans', sans-serif;
    font-size: 16px;
    color: #F0EDE4;
    outline: none;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.tk-input:focus {
    border-color: rgba(201, 168, 76, 0.5);
    box-shadow: 0 0 0 3px rgba(201, 168, 76, 0.08);
}

.tk-input::placeholder {
    color: rgba(240, 237, 228, 0.3);
}

.branch-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: 16px;
    cursor: pointer;
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.branch-card:active {
    transform: scale(0.97);
    border-color: rgba(201, 168, 76, 0.3);
}

.nav-back {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 18px;
    color: #F0EDE4;
    flex-shrink: 0;
    transition: transform 0.15s ease;
}

.nav-back:active {
    transform: scale(0.9);
}

@keyframes fadeUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes scaleIn {
    from {
        opacity: 0;
        transform: scale(0.8);
    }

    to {
        opacity: 1;
        transform: scale(1);
    }
}

@keyframes float {

    0%,
    100% {
        transform: translateY(0px);
    }

    50% {
        transform: translateY(-8px);
    }
}

@keyframes gradientShift {

    0%,
    100% {
        background-position: 0% 50%;
    }

    50% {
        background-position: 100% 50%;
    }
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

@keyframes ripple {
    0% {
        transform: scale(0.8);
        opacity: 1;
    }

    100% {
        transform: scale(2.5);
        opacity: 0;
    }
}

.neural-lines {
    position: absolute;
    inset: 0;
    overflow: hidden;
    pointer-events: none;
    opacity: 0.15;
}

.floating-card-preview {
    position: absolute;
    width: 200px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(201, 168, 76, 0.2);
    border-radius: 16px;
    padding: 14px;
    backdrop-filter: blur(20px);
    animation: float 4s ease-in-out infinite;
}

.progress-ring-svg {
    transform: rotate(-90deg);
}

.typing-cursor {
    display: inline-block;
    width: 2px;
    height: 1em;

    background: $ {
        GOLD
    }

    ;
    margin-left: 2px;
    animation: blink 0.7s ease infinite;
    vertical-align: text-bottom;
}

@keyframes blink {

    0%,
    100% {
        opacity: 1;
    }

    50% {
        opacity: 0;
    }
}

.sticky-cta {
    position: sticky;
    bottom: 0;
    padding: 16px 24px 28px;

    background: linear-gradient(to top, $ {
            NAVY2
        }

        70%, transparent);
}

`;

// ─── Animated Background ─────────────────────────────────────────────────────
function NeuralBg() {
    return (<svg style= {
                {
                position: "absolute", inset: 0, width: "100%", height: "100%", opacity: 0.07, pointerEvents: "none"
            }
        }

        viewBox="0 0 375 812" > <defs> <radialGradient id="ng1" cx="50%" cy="30%" r="50%" > <stop offset="0%" stopColor="#1E4ED8" stopOpacity="0.8" /> <stop offset="100%" stopColor="#1E4ED8" stopOpacity="0" /> </radialGradient> <radialGradient id="ng2" cx="80%" cy="70%" r="40%" > <stop offset="0%" stopColor="#C9A84C" stopOpacity="0.6" /> <stop offset="100%" stopColor="#C9A84C" stopOpacity="0" /> </radialGradient> </defs> <rect width="375" height="812" fill="url(#ng1)" /> <rect width="375" height="812" fill="url(#ng2)" /> {
            [...Array(12)].map((_, i)=> (<line key= {
                        i
                    }

                    x1= {
                        Math.sin(i * 0.8) * 200 + 187
                    }

                    y1= {
                        0
                    }

                    x2= {
                        Math.cos(i * 0.6) * 150 + 187
                    }

                    y2= {
                        812
                    }

                    stroke="#1E4ED8"
                    strokeWidth="0.5"
                    strokeOpacity="0.4"
                    />))
        }

        </svg>);
}

// ─── TrustScore Gauge ────────────────────────────────────────────────────────
function TrustGauge({
    score=84, animated=false

}) {
    const [current,
    setCurrent]=useState(animated ? 0 : score);

    useEffect(()=> {
            if ( !animated) return;
            let n=0;

            const t=setInterval(()=> {
                    n +=2;
                    setCurrent(Math.min(n, score));
                    if (n >=score) clearInterval(t);
                }

                , 25);
            return ()=> clearInterval(t);
        }

        , [animated, score]);

    const r=45;
    const circ=2 * Math.PI * r;
    const pct=current / 100;
    const dashOffset=circ * (1 - pct * 0.75); // 270 degree sweep
    const color=current>70 ? "#22C55E" : current>40 ? GOLD : "#EF4444";

    return (<div style= {
                {
                display: "flex", flexDirection: "column", alignItems: "center", gap: 4
            }
        }

        > <svg width="110" height="70" viewBox="0 0 110 70" > <circle cx="55" cy="55" r= {
            r
        }

        fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8"

        strokeDasharray= {
            circ * 0.75
        }

        strokeDashoffset= {
            0
        }

        strokeLinecap="round"

        style= {
                {
                transform: "rotate(135deg)", transformOrigin: "55px 55px"
            }
        }

        /> <circle cx="55" cy="55" r= {
            r
        }

        fill="none" stroke= {
            color
        }

        strokeWidth="8"

        strokeDasharray= {
            circ * 0.75
        }

        strokeDashoffset= {
            dashOffset
        }

        strokeLinecap="round"

        style= {
                {
                transform: "rotate(135deg)", transformOrigin: "55px 55px", transition: "stroke-dashoffset 0.05s linear, stroke 0.3s ease", filter: `drop-shadow(0 0 6px $ {
                        color
                    }

                    40)`
            }
        }

        /> <text x="55" y="52" textAnchor="middle" fill= {
            color
        }

        fontSize="20" fontWeight="800" fontFamily="Syne, sans-serif" > {
            current
        }

        </text> <text x="55" y="66" textAnchor="middle" fill="rgba(240,237,228,0.4)" fontSize="9" fontFamily="DM Sans, sans-serif" >/ 100</text> </svg> <span style= {
                {
                fontSize: 11, color: "rgba(240,237,228,0.4)", letterSpacing: "0.08em"
            }
        }

        >TRUST SCORE</span> </div>);
}

// ─── Waveform ────────────────────────────────────────────────────────────────
function Waveform({
    active

}) {
    const [bars,
    setBars]=useState(Array(28).fill(4));

    useEffect(()=> {
            if ( !active) {
                setBars(Array(28).fill(4)); return;
            }

            const id=setInterval(()=> {
                    setBars(prev=> prev.map((_, i)=> {
                                const wave=Math.sin(Date.now() / 200 + i * 0.5) * 0.5 + 0.5;
                                const rand=Math.random() * 0.4 + 0.6;
                                return Math.max(4, Math.min(48, wave * rand * 52));
                            }));
                }

                , 80);
            return ()=> clearInterval(id);
        }

        , [active]);

    return (<div style= {
                {
                display: "flex", alignItems: "center", gap: 3, height: 60, padding: "0 4px"
            }
        }

        > {
            bars.map((h, i)=> (<div key= {
                        i
                    }

                    className="waveform-bar" style= {
                            {
                            height: h, opacity: active ? 0.6 + (i % 3) * 0.1 : 0.3
                        }
                    }

                    />))
        }

        </div>);
}

// ─── CountUp ─────────────────────────────────────────────────────────────────
function CountUp({
    end, duration=1500, prefix="₹", suffix=""

}) {
    const [val,
    setVal]=useState(0);

    useEffect(()=> {
            let start=0;
            const step=end / (duration / 50);

            const id=setInterval(()=> {
                    start=Math.min(start + step, end);
                    setVal(Math.floor(start));
                    if (start >=end) clearInterval(id);
                }

                , 50);
            return ()=> clearInterval(id);
        }

        , [end, duration]);

    return <span className="count-up"> {
        prefix
    }

        {
        val.toLocaleString("en-IN")
    }

        {
        suffix
    }

    </span>;
}

// ─── Screen 1: Welcome ───────────────────────────────────────────────────────
function WelcomeScreen({
    onNext

}) {
    const [pulse,
    setPulse]=useState(false);

    useEffect(()=> {
            const t=setTimeout(()=> setPulse(true), 800); return ()=> clearTimeout(t);
        }

        , []);

    return (<div className="screen bg-deep enter" style= {
                {
                minHeight: "100%", position: "relative", overflow: "hidden"
            }
        }

        > <NeuralBg /> <div style= {
                {
                position: "absolute", top: 0, left: 0, right: 0, height: "50%", background: "radial-gradient(ellipse at 50% -20%, rgba(30,78,216,0.3) 0%, transparent 70%)"
            }
        }

        /> {
            /* Floating preview card */
        }

        <div className="floating-card-preview" style= {
                {
                top: 100, right: -20, opacity: 0.7, animationDelay: "0.5s", zIndex: 1
            }
        }

        > <div style= {
                {
                fontSize: 10, color: "rgba(240,237,228,0.4)", marginBottom: 6, letterSpacing: "0.1em"
            }
        }

        >ASSESSMENT READY</div> <div style= {
                {
                fontSize: 16, fontFamily: "Syne", fontWeight: 700, color: GOLD
            }
        }

        >₹38, 000–₹49, 000</div> <div style= {
                {
                fontSize: 11, color: "#22C55E", marginTop: 4
            }
        }

        >✓ PRE-APPROVED</div> </div> <div className="floating-card-preview" style= {
                {
                bottom: 220, left: -15, opacity: 0.6, animationDelay: "1.2s", zIndex: 1
            }
        }

        > <div style= {
                {
                fontSize: 10, color: "rgba(240,237,228,0.4)", marginBottom: 4, letterSpacing: "0.1em"
            }
        }

        >GENUINENESS</div> <div style= {
                {
                fontSize: 16, fontFamily: "Syne", fontWeight: 700, color: TEAL
            }
        }

        >94 / 100</div> </div> <div style= {
                {
                padding: "80px 28px 0", position: "relative", zIndex: 2, animation: "fadeUp 0.8s ease both"
            }
        }

        > {
            /* Logo */
        }

        <div style= {
                {
                marginBottom: 8
            }
        }

        > <div style= {
                {
                fontSize: 11, color: GOLD, letterSpacing: "0.2em", marginBottom: 6
            }
        }

        >TENZORX HACKATHON · 4D</div> <div style= {
                {
                position: "relative", display: "inline-block"
            }
        }

        > <span style= {
                {
                fontFamily: "Syne, sans-serif", fontWeight: 800, fontSize: 38, color: "#F0EDE4", letterSpacing: "-0.02em"
            }
        }

        >True</span> <span style= {
                {
                fontFamily: "Syne, sans-serif", fontWeight: 800, fontSize: 38, color: GOLD, letterSpacing: "-0.02em"
            }
        }

        >Karat</span> {
            /* Shimmer overlay */
        }

        <div style= {
                {
                position: "absolute", inset: 0, background: "linear-gradient(90deg, transparent 0%, rgba(201,168,76,0.3) 50%, transparent 100%)", backgroundSize: "200% 100%", animation: "shimmer 3s ease infinite", pointerEvents: "none"
            }
        }

        /> </div> </div> <div style= {
                {
                fontSize: 15, color: "rgba(240,237,228,0.55)", lineHeight: 1.6, marginBottom: 48, maxWidth: 280
            }
        }

        > AI-powered gold assessment.<br />Pre-qualify from home — in 5 minutes. </div> {
            /* Hero visual */
        }

        <div style= {
                {
                display: "flex", justifyContent: "center", marginBottom: 48
            }
        }

        > <div style= {
                {
                width: 200, height: 200, borderRadius: "50%", background: "radial-gradient(circle, rgba(201,168,76,0.15) 0%, rgba(30,78,216,0.08) 50%, transparent 70%)", border: "1px solid rgba(201,168,76,0.2)", display: "flex", alignItems: "center", justifyContent: "center", position: "relative"
            }
        }

        > <div style= {
                {
                position: "absolute", inset: -12, borderRadius: "50%", border: "1px solid rgba(201,168,76,0.1)", animation: pulse ? "ripple 2.5s ease infinite" : "none"
            }
        }

        /> <div style= {
                {
                position: "absolute", inset: -24, borderRadius: "50%", border: "1px solid rgba(201,168,76,0.06)", animation: pulse ? "ripple 2.5s ease 0.5s infinite" : "none"
            }
        }

        /> <div style= {
                {
                fontSize: 72, animation: "float 3s ease-in-out infinite"
            }
        }

        >💛</div> </div> </div> {
            /* Feature pills */
        }

        <div style= {
                {
                display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 40
            }
        }

        > {
            ["Vision AI", "Audio FFT", "6-Layer Fraud", "Live Price"].map(f=> (<span key= {
                        f
                    }

                    style= {
                            {
                            background: "rgba(201,168,76,0.08)", border: "1px solid rgba(201,168,76,0.2)", borderRadius: 20, padding: "5px 12px", fontSize: 12, color: GOLD, letterSpacing: "0.03em"
                        }
                    }

                    > {
                        f
                    }

                    </span>))
        }

        </div> </div> <div className="sticky-cta" style= {
                {
                position: "relative", zIndex: 2
            }
        }

        > <button className="tk-btn-primary" onClick= {
            onNext
        }

        style= {
                {
                boxShadow: pulse ? `0 0 30px rgba(201, 168, 76, 0.3)` : "none", transition: "box-shadow 1s ease", animation: "fadeUp 0.8s 0.4s ease both"
            }
        }

        > Begin Assessment → </button> <div style= {
                {
                textAlign: "center", marginTop: 12, fontSize: 12, color: "rgba(240,237,228,0.3)"
            }
        }

        > No branch visit required </div> </div> </div>);
}

// ─── Screen 2: Customer Input (Conversational) ──────────────────────────────
function CustomerInputScreen({
    onNext, onBack

}) {
    const [step,
    setStep]=useState(0);

    const [values,
    setValues]=useState({
        name: "", phone: "", otp: ["", "", "", ""]
    });
const [otpState,
setOtpState]=useState("idle"); // idle | filling | success
const [currentVal,
setCurrentVal]=useState("");

const steps=[ {
    id: "name", prompt: "Let's get started — what should we call you?", placeholder: "Your name", type: "text"
}

,
{
id: "phone", prompt: "What's your mobile number?", placeholder: "+91 98765 43210", type: "tel"
}

,
];

const handleNext=()=> {
    if (step < steps.length - 1) {
        setValues(v=> ({
                ...v, [steps[step].id]: currentVal
            }));
    setCurrentVal("");
    setStep(s=> s + 1);
}

else {
    setValues(v=> ({
            ...v, phone: currentVal
        }));
setStep(2); // OTP step
simulateOTP();
}
}

;

const simulateOTP=()=> {
    const code=["6",
    "2",
    "4",
    "1"];
    setOtpState("filling");

    code.forEach((d, i)=> {
            setTimeout(()=> {
                    setValues(v=> {
                            const otp=[...v.otp];
                            otp[i]=d;

                            return {
                                ...v, otp
                            }

                            ;
                        });
                }

                , 400 + i * 300);
        });

    setTimeout(()=> {
            setOtpState("success");
            setTimeout(onNext, 800);
        }

        , 2200);
}

;

return (<div className="screen bg-deep enter" style= {
            {
            minHeight: "100%", position: "relative"
        }
    }

    > <NeuralBg /> <div style= {
            {
            padding: "56px 24px 0", position: "relative", zIndex: 1
        }
    }

    > <div style= {
            {
            display: "flex", alignItems: "center", gap: 12, marginBottom: 32
        }
    }

    > <div className="nav-back" onClick= {
        onBack
    }

    >←</div> <div className="step-bar" style= {
            {
            padding: 0, flex: 1
        }
    }

    > {
        [0, 1, 2].map(i=> (<div key= {
                    i
                }

                className= {
                    `step-dot $ {
                        i < step ? "done" : i===step ? "active" : ""
                    }

                    `
                }

                />))
    }

    </div> </div> {
        step < 2 ? (<div key= {
                step
            }

            style= {
                    {
                    animation: "fadeUp 0.4s ease both"
                }
            }

            > <div style= {
                    {
                    fontSize: 12, color: GOLD, letterSpacing: "0.15em", marginBottom: 10
                }
            }

            >STEP {
                step + 1
            }

            OF 3</div> <h2 style= {
                    {
                    fontFamily: "Syne", fontWeight: 700, fontSize: 22, color: "#F0EDE4", lineHeight: 1.35, marginBottom: 32
                }
            }

            > {
                steps[step].prompt
            }

            </h2> <input className="tk-input"

            type= {
                steps[step].type
            }

            placeholder= {
                steps[step].placeholder
            }

            value= {
                currentVal
            }

            onChange= {
                e=> setCurrentVal(e.target.value)
            }

            autoFocus /> <button className="tk-btn-primary" onClick= {
                handleNext
            }

            style= {
                    {
                    marginTop: 20
                }
            }

            disabled= {
                !currentVal.trim()
            }

            > Continue → </button> </div>) : (<div style= {
                    {
                    animation: "fadeUp 0.4s ease both"
                }
            }

            > <div style= {
                    {
                    fontSize: 12, color: GOLD, letterSpacing: "0.15em", marginBottom: 10
                }
            }

            >VERIFICATION</div> <h2 style= {
                    {
                    fontFamily: "Syne", fontWeight: 700, fontSize: 22, color: "#F0EDE4", lineHeight: 1.35, marginBottom: 8
                }
            }

            > We sent a code to your number </h2> <p style= {
                    {
                    color: "rgba(240,237,228,0.5)", fontSize: 14, marginBottom: 36
                }
            }

            > Filling automatically… </p> <div style= {
                    {
                    display: "flex", gap: 10, justifyContent: "center", marginBottom: 40
                }
            }

            > {
                values.otp.map((d, i)=> (<div key= {
                            i
                        }

                        className= {
                            `otp-box $ {
                                d ? (otpState==="success" ? "success" : "filled") : ""
                            }

                            `
                        }

                        > {
                            d
                        }

                            {
                            otpState==="success" && d && <div style= {
                                    {
                                    position: "absolute", fontSize: 10
                                }
                            }

                            />
                        }

                        </div>))
            }

            </div> {
                otpState==="success" && (<div style= {
                            {
                            textAlign: "center", animation: "scaleIn 0.4s ease both"
                        }
                    }

                    > <div style= {
                            {
                            width: 48, height: 48, borderRadius: "50%", background: "rgba(34,197,94,0.15)", border: "2px solid #22C55E", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 12px", fontSize: 22
                        }
                    }

                    >✓</div> <div style= {
                            {
                            color: "#22C55E", fontFamily: "Syne", fontWeight: 600, fontSize: 16
                        }
                    }

                    >Verified !</div> </div>)
            }

            </div>)
    }

        {
        /* Welcome back card for context */
    }

        {
        values.name && (<div className="glass-card" style= {
                    {
                    padding: 14, marginTop: 24
                }
            }

            > <div style= {
                    {
                    fontSize: 12, color: "rgba(240,237,228,0.4)"
                }
            }

            >Logged in as</div> <div style= {
                    {
                    fontFamily: "Syne", fontWeight: 600, color: "#F0EDE4", marginTop: 2
                }
            }

            > {
                values.name
            }

            </div> </div>)
    }

    </div> </div>);
}

// ─── Screen 3: Capture ───────────────────────────────────────────────────────
function CaptureScreen({ onNext, onBack, setApiResult }) {
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
    };

    return (<div className="screen bg-deep enter" style= {
                {
                minHeight: "100%", position: "relative", background: "#050810"
            }
        }

        > {
            /* Flash effect */
        }

            {
            flashOn && <div style= {
                    {
                    position: "absolute", inset: 0, background: "white", opacity: 0.6, zIndex: 10, animation: "scaleIn 0.1s ease", pointerEvents: "none"
                }
            }

            />
        }

            {
            /* Fake camera feed */
        }

        <div style= {
                {
                position: "absolute", inset: 0, background: "linear-gradient(145deg, #060A12 0%, #0A1020 50%, #050C18 100%)"
            }
        }

        > {
            /* Simulated gold item */
        }

        <div style= {
                {
                position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)", width: 120, height: 90, borderRadius: "50%", background: "radial-gradient(ellipse, #C9A84C 0%, #8B6914 60%, #5A4008 100%)", opacity: state==="detected" ? 0.9 : 0.7, boxShadow: state==="detected" ? "0 0 40px rgba(201,168,76,0.4)" : "none", transition: "all 0.5s ease"
            }
        }

        /> </div> {
            /* Top bar */
        }

        <div style= {
                {
                position: "absolute", top: 0, left: 0, right: 0, padding: "52px 24px 16px", background: "linear-gradient(to bottom, rgba(5,8,16,0.9), transparent)", zIndex: 5, display: "flex", alignItems: "center", gap: 12
            }
        }

        > <div className="nav-back" onClick= {
            onBack
        }

        style= {
                {
                background: "rgba(0,0,0,0.5)"
            }
        }

        >←</div> <div> <div style= {
                {
                fontFamily: "Syne", fontWeight: 700, fontSize: 15, color: "#F0EDE4"
            }
        }

        >Capture Gold Item</div> <div style= {
                {
                fontSize: 11, color: GOLD, letterSpacing: "0.1em"
            }
        }

        >LIVE CAMERA · SECURE SESSION</div> </div> <div style= {
                {
                marginLeft: "auto", background: "rgba(239,68,68,0.15)", border: "1px solid rgba(239,68,68,0.3)", borderRadius: 8, padding: "4px 10px", fontSize: 11, color: "#EF4444"
            }
        }

        >● REC</div> </div> {
            /* Scan overlay */
        }

        <div className="camera-overlay" style= {
                {
                zIndex: 3
            }
        }

        > <div style= {
                {
                position: "relative"
            }
        }

        > <input type="file" accept="image/*" capture="environment" ref={fileRef} style={{display:'none'}} onChange={handleFile} />
        <div onClick={() => fileRef.current?.click()} style={{cursor: 'pointer'}} className={`scan-ring ${state==="detected" ? "detected" : ""}`}> <div className="corner-tl" /> <div className="corner-tr" /> <div className="corner-bl" /> <div className="corner-br" /> {
            /* Grid lines */
        }

        <svg style= {
                {
                position: "absolute", inset: 0, width: "100%", height: "100%", opacity: 0.3
            }
        }

        viewBox="0 0 220 220" > <line x1="73" y1="0" x2="73" y2="220" stroke= {
            GOLD
        }

        strokeWidth="0.5" /> <line x1="147" y1="0" x2="147" y2="220" stroke= {
            GOLD
        }

        strokeWidth="0.5" /> <line x1="0" y1="73" x2="220" y2="73" stroke= {
            GOLD
        }

        strokeWidth="0.5" /> <line x1="0" y1="147" x2="220" y2="147" stroke= {
            GOLD
        }

        strokeWidth="0.5" /> {
            state==="detected" && (<> <rect x="50" y="70" width="120" height="80" rx="4" fill="none" stroke= {
                    TEAL
                }

                strokeWidth="1.5" strokeDasharray="4 2" /> <circle cx="110" cy="110" r="3" fill= {
                    TEAL
                }

                /> </>)
        }

        </svg> </div> {
            /* AI indicators */
        }

            {
            state==="detected" && (<div style= {
                        {
                        position: "absolute", bottom: -60, left: "50%", transform: "translateX(-50%)", whiteSpace: "nowrap", animation: "fadeUp 0.3s ease both"
                    }
                }

                > <div style= {
                        {
                        background: "rgba(14,207,207,0.12)", border: "1px solid rgba(14,207,207,0.3)", borderRadius: 20, padding: "6px 16px", fontSize: 12, color: TEAL, fontWeight: 500
                    }
                }

                > ◉ Object Detected — BIS Hallmark Visible </div> </div>)
        }

        </div> </div> {
            /* Bottom message */
        }

        <div style= {
                {
                position: "absolute", bottom: 0, left: 0, right: 0, padding: "16px 24px 40px", background: "linear-gradient(to top, rgba(5,8,16,0.95), transparent)", zIndex: 5
            }
        }

        > <p style= {
                {
                color: "#F0EDE4", fontSize: 15, textAlign: "center", fontWeight: 500
            }
        }

        > {
            msg
        }

        </p> <div style= {
                {
                display: "flex", gap: 8, justifyContent: "center", marginTop: 12
            }
        }

        > {
            ["Hallmark", "Weight", "Texture"].map((tag, i)=> (<span key= {
                        tag
                    }

                    style= {
                            {
                            fontSize: 11, color: state==="detected" && i===0 ? TEAL : "rgba(240,237,228,0.3)", background: state==="detected" && i===0 ? "rgba(14,207,207,0.1)" : "rgba(255,255,255,0.04)", border: `1px solid $ {
                                state==="detected" && i===0 ? "rgba(14,207,207,0.3)" : "rgba(255,255,255,0.08)"
                            }

                            `, borderRadius: 20, padding: "4px 10px", transition: "all 0.3s ease"
                        }
                    }

                    > {
                        state==="detected" && i===0 ? "✓ " : ""
                    }

                        {
                        tag
                    }

                    </span>))
        }

        </div> </div> </div>);
}

// ─── Screen 4: Audio Tap ─────────────────────────────────────────────────────
function AudioScreen({
    onNext, onBack

}) {
    const [state,
    setState]=useState("idle"); // idle | recording | done
    const [seconds,
    setSeconds]=useState(0);

    const startRecording=()=> {
        setState("recording");
        let s=0;

        const id=setInterval(()=> {
                s++;
                setSeconds(s);

                if (s >=5) {
                    clearInterval(id);
                    setState("done");
                    setTimeout(onNext, 1200);
                }
            }

            , 1000);
    }

    ;

    return (<div className="screen bg-deep enter" style= {
                {
                minHeight: "100%", position: "relative"
            }
        }

        > <NeuralBg /> <div style= {
                {
                padding: "56px 24px 0", position: "relative", zIndex: 1
            }
        }

        > <div style= {
                {
                display: "flex", alignItems: "center", gap: 12, marginBottom: 40
            }
        }

        > <div className="nav-back" onClick= {
            onBack
        }

        >←</div> <div> <div style= {
                {
                fontFamily: "Syne", fontWeight: 700, fontSize: 17, color: "#F0EDE4"
            }
        }

        >Audio Tap Test</div> <div style= {
                {
                fontSize: 11, color: GOLD, letterSpacing: "0.1em"
            }
        }

        >FFT ACOUSTIC ANALYSIS</div> </div> </div> {
            /* Instruction */
        }

        <div className="glass-card" style= {
                {
                padding: 20, marginBottom: 32
            }
        }

        > <div style= {
                {
                fontSize: 13, color: "rgba(240,237,228,0.5)", lineHeight: 1.7
            }
        }

        > Gently tap your gold piece 2–3 times while recording. Our AI reads the acoustic signature to distinguish <span style= {
                {
                color: GOLD
            }
        }

        >pure gold</span> from brass or plated metals. </div> </div> {
            /* Central recording UI */
        }

        <div style= {
                {
                display: "flex", flexDirection: "column", alignItems: "center", gap: 28
            }
        }

        > {
            /* Record button with ripple */
        }

        <div style= {
                {
                position: "relative"
            }
        }

        > {
            state==="recording" && (<> <div style= {
                        {
                        position: "absolute", inset: -16, borderRadius: "50%", border: "2px solid rgba(239,68,68,0.4)", animation: "ripple 1.5s ease infinite"
                    }
                }

                /> <div style= {
                        {
                        position: "absolute", inset: -8, borderRadius: "50%", border: "2px solid rgba(239,68,68,0.2)", animation: "ripple 1.5s ease 0.4s infinite"
                    }
                }

                /> </>)
        }

        <button onClick= {
            state==="idle" ? startRecording : undefined
        }

        style= {
                {

                width: 88, height: 88, borderRadius: "50%",
                background: state==="recording" ? "linear-gradient(135deg, #EF4444, #B91C1C)" : state==="done" ? "linear-gradient(135deg, #22C55E, #15803D)" : `linear-gradient(135deg, $ {
                        GOLD
                    }

                    , #A87D28)`,
                border: "none", cursor: state==="idle" ? "pointer" : "default",
                display: "flex", alignItems: "center", justifyContent: "center", fontSize: 32,
                boxShadow: state==="recording" ? "0 0 40px rgba(239,68,68,0.3)" : state==="done" ? "0 0 40px rgba(34,197,94,0.3)" : "0 0 30px rgba(201,168,76,0.2)",
                transition: "all 0.4s ease"
            }
        }

        > {
            state==="idle" ? "🎙" : state==="recording" ? "⏹" : "✓"
        }

        </button> </div> {
            state==="idle" && <p style= {
                    {
                    color: "rgba(240,237,228,0.6)", fontSize: 14, textAlign: "center"
                }
            }

            >Tap to begin recording</p>
        }

            {
            state==="recording" && <div style= {
                    {
                    color: "#EF4444", fontFamily: "Syne", fontWeight: 600, fontSize: 15
                }
            }

            >Recording… {
                5 - seconds
            }

            s left</div>
        }

            {
            state==="done" && <div style= {
                    {
                    color: "#22C55E", fontFamily: "Syne", fontWeight: 600, fontSize: 15, animation: "scaleIn 0.4s ease both"
                }
            }

            >✓ Acoustic signature captured</div>
        }

            {
            /* Waveform */
        }

        <div className="glass-card" style= {
                {
                width: "100%", padding: "16px 20px"
            }
        }

        > <div style= {
                {
                fontSize: 11, color: "rgba(240,237,228,0.4)", marginBottom: 10, letterSpacing: "0.1em"
            }
        }

        >AUDIO FFT VISUALIZATION</div> <Waveform active= {
            state==="recording"
        }

        /> {
            state==="done" && (<div style= {
                        {
                        display: "flex", gap: 8, marginTop: 12, animation: "fadeUp 0.4s ease both"
                    }
                }

                > {
                    [["GOLD", "#22C55E", 72], ["BRASS", "#EF4444", 18], ["PLATED", "#F59E0B", 10]].map(([label, color, pct])=> (<div key= {
                                label
                            }

                            style= {
                                    {
                                    flex: 1, background: "rgba(255,255,255,0.04)", borderRadius: 10, padding: "8px 10px", textAlign: "center"
                                }
                            }

                            > <div style= {
                                    {
                                    fontSize: 16, fontFamily: "Syne", fontWeight: 700, color
                                }
                            }

                            > {
                                pct
                            }

                            %</div> <div style= {
                                    {
                                    fontSize: 10, color: "rgba(240,237,228,0.4)", marginTop: 2
                                }
                            }

                            > {
                                label
                            }

                            </div> </div>))
                }

                </div>)
        }

        </div> </div> </div> </div>);
}

// ─── Screen 5: Analysis ──────────────────────────────────────────────────────
function AnalysisScreen({
    onNext

}) {
    const [visibleSteps,
    setVisibleSteps]=useState([]);

    const steps=[ {
        icon: "👁", label: "Reading hallmark depth…", detail: "BIS 916 hallmark detected", delay: 400, done: false
    }

    ,
    {
    icon: "🔊", label: "Comparing acoustic signature…", detail: "Gold resonance pattern matched", delay: 1200, done: false
}

,
{
icon: "⚖", label: "Estimating weight via coin reference…", detail: "8.2g – 10.5g range confirmed", delay: 2000, done: false
}

,
{
icon: "💰", label: "Fetching live gold price…", detail: "₹7,180/gram · goldapi.io", delay: 2800, done: false
}

,
{
icon: "🛡", label: "Running 6-layer anti-spoofing…", detail: "EXIF · ELA · OTP · Live feed verified", delay: 3600, done: false
}

,
{
icon: "📊", label: "Calibrating confidence score…", detail: "Fusion model: 94/100 genuineness", delay: 4400, done: false
}

,
];

useEffect(()=> {
        steps.forEach((s, i)=> {
                setTimeout(()=> setVisibleSteps(v=> [...v, i]), s.delay);
            });
        setTimeout(onNext, 5600);
    }

    , []);

const totalProgress=visibleSteps.length / steps.length;

return (<div className="screen bg-deep enter" style= {
            {
            minHeight: "100%", position: "relative"
        }
    }

    > <NeuralBg /> {
        /* Animated grid background */
    }

    <div style= {
            {
            position: "absolute", inset: 0, opacity: 0.05, backgroundImage: "linear-gradient(rgba(30,78,216,0.8) 1px, transparent 1px), linear-gradient(90deg, rgba(30,78,216,0.8) 1px, transparent 1px)", backgroundSize: "32px 32px", pointerEvents: "none"
        }
    }

    /> <div style= {
            {
            padding: "56px 24px 0", position: "relative", zIndex: 1
        }
    }

    > <div style= {
            {
            marginBottom: 32
        }
    }

    > <div style= {
            {
            fontSize: 12, color: GOLD, letterSpacing: "0.15em", marginBottom: 8
        }
    }

    >AI ANALYSIS</div> <h2 style= {
            {
            fontFamily: "Syne", fontWeight: 800, fontSize: 26, color: "#F0EDE4"
        }
    }

    >A system is thinking<br />in real time…</h2> </div> {
        /* Progress bar */
    }

    <div style= {
            {
            height: 3, background: "rgba(201,168,76,0.1)", borderRadius: 3, marginBottom: 36, overflow: "hidden"
        }
    }

    > <div style= {
            {
            height: "100%", background: `linear-gradient(90deg, $ {
                    GOLD
                }

                , $ {
                    TEAL

                })`, width: `$ {
                totalProgress * 100
            }

            %`, borderRadius: 3, transition: "width 0.5s ease", boxShadow: `0 0 8px rgba(201, 168, 76, 0.5)`
        }
    }

    /> </div> {
        /* Steps */
    }

    <div style= {
            {
            display: "flex", flexDirection: "column", gap: 18
        }
    }

    > {
        steps.map((s, i)=> (<div key= {
                    i
                }

                className= {
                    `analysis-step $ {
                        visibleSteps.includes(i) ? "visible" : ""
                    }

                    `
                }

                > <div className= {
                    `step-icon-ring $ {
                        visibleSteps.includes(i) ? (visibleSteps.length > i + 1 ? "done" : "active") : ""
                    }

                    `
                }

                > {
                    visibleSteps.length > i + 1 ? "✓" : s.icon
                }

                </div> <div style= {
                        {
                        flex: 1
                    }
                }

                > <div style= {
                        {
                        fontSize: 14, color: "#F0EDE4", fontWeight: 500, marginBottom: 3
                    }
                }

                > {
                    s.label
                }

                    {
                    visibleSteps.length===i + 1 && <span className="typing-cursor" />
                }

                </div> {
                    visibleSteps.length > i + 1 && (<div style= {
                                {
                                fontSize: 12, color: TEAL, animation: "fadeUp 0.3s ease both"
                            }
                        }

                        > {
                            s.detail
                        }

                        </div>)
                }

                </div> </div>))
    }

    </div> </div> </div>);
}

// ─── Screen 6: Result ─────────────────────────────────────────────────────────
function ResultScreen({ onNext, onBack, apiResult }) {
    const [mounted,
    setMounted]=useState(false);

    useEffect(()=> {
            const t=setTimeout(()=> setMounted(true), 100); return ()=> clearTimeout(t);
        }

        , []);

    return (<div className="screen bg-deep enter" style= {
                {
                minHeight: "100%"
            }
        }

        > <NeuralBg /> <div style= {
                {
                padding: "52px 24px 0", position: "relative", zIndex: 1
            }
        }

        > {
            /* Header */
        }

        <div style= {
                {
                display: "flex", alignItems: "center", gap: 12, marginBottom: 28
            }
        }

        > <div className="nav-back" onClick= {
            onBack
        }

        >←</div> <div> <div style= {
                {
                fontFamily: "Syne", fontWeight: 700, fontSize: 15, color: "#F0EDE4"
            }
        }

        >TrueKarat Report</div> <div style= {
                {
                fontSize: 11, color: "rgba(240,237,228,0.4)"
            }
        }

        >Gold Bangle · Session #TK-2491</div> </div> <div style= {
                {
                marginLeft: "auto", fontSize: 11, color: GOLD
            }
        }

        >4m 12s</div> </div> {
            /* Verdict banner */
        }

            {
            mounted && (<div className="verdict-banner" style= {
                        {
                        marginBottom: 24, animation: "scaleIn 0.5s cubic-bezier(0.34,1.56,0.64,1) both"
                    }
                }

                > <div style= {
                        {
                        width: 44, height: 44, borderRadius: "50%", background: "rgba(34,197,94,0.15)", border: "2px solid #22C55E", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20, flexShrink: 0
                    }
                }

                >✓</div> <div> <div style= {
                        {
                        fontFamily: "Syne", fontWeight: 800, fontSize: 18, color: "#22C55E"
                    }
                }

                >{apiResult?.verdict || "PRE-APPROVED"}</div> <div style= {
                        {
                        fontSize: 12, color: "rgba(240,237,228,0.5)", marginTop: 2
                    }
                }

                >Eligible for gold loan — visit any branch</div> </div> </div>)
        }

            {
            /* Main value */
        }

            {
            mounted && (<div className="result-value-card shimmer" style= {
                        {
                        marginBottom: 16, textAlign: "center", padding: "20px", animation: "fadeUp 0.5s 0.2s ease both"
                    }
                }

                > <div style= {
                        {
                        fontSize: 12, color: "rgba(240,237,228,0.4)", letterSpacing: "0.12em", marginBottom: 6
                    }
                }

                >ESTIMATED GOLD VALUE</div> <div style= {
                        {
                        fontSize: 30, fontFamily: "Syne", fontWeight: 800
                    }
                }

                > <CountUp end={apiResult?.min_value || 38000} prefix="₹" duration={1200} /> – <CountUp end={apiResult?.max_value || 49000}

                prefix="₹" duration= {
                    1600
                }

                /> </div> <div style= {
                        {
                        fontSize: 13, color: "rgba(240,237,228,0.4)", marginTop: 4
                    }
                }

                >Based on live gold rate ₹7, 180/g</div> </div>)
        }

            {
            /* Loan + Trust row */
        }

            {
            mounted && (<div style= {
                        {
                        display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 16, animation: "fadeUp 0.5s 0.35s ease both"
                    }
                }

                > <div className="result-value-card" style= {
                        {
                        textAlign: "center"
                    }
                }

                > <div style= {
                        {
                        fontSize: 11, color: "rgba(240,237,228,0.4)", marginBottom: 6
                    }
                }

                >LOAN ELIGIBLE</div> <div style= {
                        {
                        fontFamily: "Syne", fontWeight: 700, fontSize: 16, color: GOLD
                    }
                }

                >{apiResult ? `₹${apiResult.min_value}` : "₹32,300"}</div> <div style= {
                        {
                        fontSize: 10, color: "rgba(240,237,228,0.35)", marginTop: 4
                    }
                }

                >RBI LTV 75%</div> </div> <div className="result-value-card" style= {
                        {
                        display: "flex", flexDirection: "column", alignItems: "center"
                    }
                }

                > <TrustGauge score={apiResult?.trustScore || 84}

                animated= {
                    mounted
                }

                /> </div> </div>)
        }

            {
            /* Details grid */
        }

            {
            mounted && (<div className="glass-card" style= {
                        {
                        padding: 16, marginBottom: 16, animation: "fadeUp 0.5s 0.5s ease both"
                    }
                }

                > {

                    [ ["Jewelry Type", apiResult?.type || "Chain / Necklace", GOLD],
                    ["Purity Band", apiResult?.purity || "22K", GOLD],
                    ["Est. Weight", apiResult?.weight || "10.0g", "#F0EDE4"],
                    ["Genuineness", (apiResult?.trustScore || 84) + " / 100", TEAL],
                    ["Spoofing Risk", "LOW", "#22C55E"],
                    ].map(([k, v, c])=> (<div key= {
                                k
                            }

                            style= {
                                    {
                                    display: "flex", justifyContent: "space-between", alignItems: "center", padding: "9px 0", borderBottom: "1px solid rgba(255,255,255,0.05)"
                                }
                            }

                            > <span style= {
                                    {
                                    fontSize: 13, color: "rgba(240,237,228,0.5)"
                                }
                            }

                            > {
                                k
                            }

                            </span> <span style= {
                                    {
                                    fontSize: 13, fontWeight: 600, color: c
                                }
                            }

                            > {
                                v
                            }

                            </span> </div>))
                }

                </div>)
        }

        </div> <div className="sticky-cta" style= {
                {
                position: "sticky", bottom: 0
            }
        }

        > <button className="tk-btn-primary" onClick= {
            onNext
        }

        style= {
                {
                animation: "fadeUp 0.5s 0.6s ease both"
            }
        }

        > Find a Branch → Proceed to Loan </button> </div> </div>);
}

// ─── Screen 7: Branch Flow ────────────────────────────────────────────────────
function BranchScreen({
    onBack

}) {
    const branches=[ {
        name: "Koramangala Branch", dist: "1.2 km", time: "9 AM – 6 PM", badge: "Open Now", color: "#22C55E"
    }

    ,
    {
    name: "Indiranagar Branch", dist: "3.1 km", time: "9 AM – 5 PM", badge: "Open Now", color: "#22C55E"
}

,
{
name: "Whitefield Branch", dist: "8.4 km", time: "10 AM – 4 PM", badge: "Closes Soon", color: "#F59E0B"
}

,
];
const [selected,
setSelected]=useState(null);

return (<div className="screen bg-deep enter" style= {
            {
            minHeight: "100%"
        }
    }

    > <NeuralBg /> <div style= {
            {
            padding: "56px 24px 0", position: "relative", zIndex: 1
        }
    }

    > <div style= {
            {
            display: "flex", alignItems: "center", gap: 12, marginBottom: 28
        }
    }

    > <div className="nav-back" onClick= {
        onBack
    }

    >←</div> <div> <div style= {
            {
            fontFamily: "Syne", fontWeight: 700, fontSize: 17, color: "#F0EDE4"
        }
    }

    >Choose a Branch</div> <div style= {
            {
            fontSize: 11, color: GOLD, letterSpacing: "0.08em"
        }
    }

    >BENGALURU · 3 BRANCHES NEARBY</div> </div> </div> {
        /* Fake map */
    }

    <div style= {
            {
            borderRadius: 20, overflow: "hidden", marginBottom: 24, height: 160, position: "relative", background: "linear-gradient(135deg, #0D1A2E 0%, #0A1424 100%)", border: "1px solid rgba(201,168,76,0.1)"
        }
    }

    > <svg style= {
            {
            width: "100%", height: "100%"
        }
    }

    viewBox="0 0 327 160" > {
        /* Map grid lines */
    }

        {
        [40, 80, 120].map(y=> <line key= {
                y
            }

            x1="0" y1= {
                y
            }

            x2="327" y2= {
                y
            }

            stroke="rgba(255,255,255,0.05)" strokeWidth="1" />)
    }

        {
        [60, 120, 180, 240, 300].map(x=> <line key= {
                x
            }

            x1= {
                x
            }

            y1="0" x2= {
                x
            }

            y2="160" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />)
    }

        {
        /* Roads */
    }

    <path d="M0,80 Q80,70 163,80 Q240,90 327,80" stroke="rgba(201,168,76,0.2)" strokeWidth="2.5" fill="none" /> <path d="M163,0 Q155,40 163,80 Q170,120 163,160" stroke="rgba(201,168,76,0.15)" strokeWidth="2" fill="none" /> {
        /* Pins */
    }

        {
        [[80, 60, "#22C55E"], [200, 90, "#22C55E"], [280, 50, "#F59E0B"]].map(([x, y, c], i)=> (<g key= {
                    i
                }

                > <circle cx= {
                    x
                }

                cy= {
                    y
                }

                r="8" fill= {
                    c
                }

                fillOpacity="0.2" /> <circle cx= {
                    x
                }

                cy= {
                    y
                }

                r="4" fill= {
                    c
                }

                /> <text x= {
                    x
                }

                y= {
                    y - 14
                }

                textAnchor="middle" fill="white" fontSize="9" fontFamily="DM Sans" > {
                    i + 1
                }

                </text> </g>))
    }

        {
        /* You are here */
    }

    <circle cx="163" cy="80" r="6" fill= {
        BLUE_GLOW
    }

    /> <circle cx="163" cy="80" r="12" fill= {
        BLUE_GLOW
    }

    fillOpacity="0.2" /> <text x="163" y="100" textAnchor="middle" fill= {
        GOLD
    }

    fontSize="8" fontFamily="DM Sans" >You</text> </svg> </div> {
        /* Branch cards */
    }

    <div style= {
            {
            display: "flex", flexDirection: "column", gap: 12, marginBottom: 24
        }
    }

    > {
        branches.map((b, i)=> (<div key= {
                    i
                }

                className="branch-card"

                onClick= {
                    ()=> setSelected(i)
                }

                style= {
                        {

                        borderColor: selected===i ? `rgba(201, 168, 76, 0.4)` : "rgba(255,255,255,0.08)",
                        background: selected===i ? "rgba(201,168,76,0.06)" : "rgba(255,255,255,0.04)",
                        animation: `fadeUp 0.4s $ {
                            i * 0.1
                        }

                        s ease both`
                    }
                }

                > <div style= {
                        {
                        display: "flex", alignItems: "flex-start", justifyContent: "space-between"
                    }
                }

                > <div> <div style= {
                        {
                        fontFamily: "Syne", fontWeight: 600, fontSize: 15, color: "#F0EDE4", marginBottom: 4
                    }
                }

                > {
                    b.name
                }

                </div> <div style= {
                        {
                        fontSize: 12, color: "rgba(240,237,228,0.5)"
                    }
                }

                > {
                    b.time
                }

                </div> </div> <div style= {
                        {
                        display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6
                    }
                }

                > <span style= {
                        {
                        background: `$ {
                            b.color
                        }

                        18`, border: `1px solid $ {
                            b.color
                        }

                        40`, color: b.color, fontSize: 10, padding: "3px 10px", borderRadius: 20, fontWeight: 600
                    }
                }

                > {
                    b.badge
                }

                </span> <span style= {
                        {
                        fontSize: 12, color: GOLD
                    }
                }

                > {
                    b.dist
                }

                </span> </div> </div> {
                    selected===i && (<div style= {
                                {
                                marginTop: 12, paddingTop: 12, borderTop: "1px solid rgba(201,168,76,0.15)", display: "flex", gap: 8, animation: "fadeUp 0.2s ease both"
                            }
                        }

                        > <button className="tk-btn-ghost" style= {
                                {
                                padding: "8px 14px", fontSize: 12
                            }
                        }

                        >Get Directions</button> <button className="tk-btn-primary" style= {
                                {
                                padding: "8px 14px", fontSize: 12
                            }
                        }

                        >Book Slot</button> </div>)
                }

                </div>))
    }

    </div> </div> <div className="sticky-cta" style= {
            {
            position: "sticky", bottom: 0
        }
    }

    > <button className="tk-btn-primary" disabled= {
        selected===null
    }

    style= {
            {
            opacity: selected !==null ? 1 : 0.4
        }
    }

    > Confirm Branch & Book Slot → </button> </div> </div>);
}

// ─── Main App ─────────────────────────────────────────────────────────────────
export default function App() {
    const [screen, setScreen] = useState(0);
    const [apiResult, setApiResult] = useState(null);

    const screens=[ <WelcomeScreen onNext= {
        ()=>setScreen(1)
    }

    />,
    <CustomerInputScreen onNext= {
        ()=>setScreen(2)
    }

    onBack= {
        ()=>setScreen(0)
    }

    />,
    <CaptureScreen setApiResult={setApiResult} onNext= {
        ()=>setScreen(3)
    }

    onBack= {
        ()=>setScreen(1)
    }

    />,
    <AudioScreen onNext= {
        ()=>setScreen(4)
    }

    onBack= {
        ()=>setScreen(2)
    }

    />,
    <AnalysisScreen onNext= {
        ()=>setScreen(5)
    }

    />,
    <ResultScreen apiResult={apiResult} onNext= {
        ()=>setScreen(6)
    }

    onBack= {
        ()=>setScreen(0)
    }

    />,
    <BranchScreen onBack= {
        ()=>setScreen(5)
    }

    />,
    ];

    const labels=["Welcome",
    "Identity",
    "Capture",
    "Audio",
    "Analysis",
    "Result",
    "Branch"];

    return (<> <style> {
            css
        }

        </style> <div className="tk-app" > <div style= {
                {
                display: "flex", flexDirection: "column", alignItems: "center", gap: 20
            }
        }

        > {
            /* Screen navigation dots */
        }

        <div style= {
                {
                display: "flex", gap: 6, marginBottom: -8
            }
        }

        > {
            screens.map((_, i)=> (<button key= {
                        i
                    }

                    onClick= {
                        ()=> setScreen(i)
                    }

                    title= {
                        labels[i]
                    }

                    style= {
                            {
                            width: i===screen ? 24 : 8,
                            height: 8,
                            borderRadius: 4,
                            border: "none",
                            background: i===screen ? GOLD : "rgba(201,168,76,0.25)",
                            cursor: "pointer",
                            transition: "all 0.3s ease",
                            padding: 0,
                        }
                    }

                    />))
        }

        </div> <div className="phone-frame" > {
            screens[screen]
        }

        </div> <div style= {
                {
                color: "rgba(201,168,76,0.4)", fontSize: 12, letterSpacing: "0.1em", fontFamily: "DM Sans"
            }
        }

        > TRUEKARAT · SCREEN {
            screen + 1
        }

        /7 · {
            labels[screen].toUpperCase()
        }

        </div> </div> </div> </>);
}