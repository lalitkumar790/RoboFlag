"""Real Chromium smoke test against generated static dashboard."""
import subprocess
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

def main():
    root=Path(__file__).resolve().parents[1]
    server=subprocess.Popen([sys.executable,"-m","http.server","8765","--bind","127.0.0.1","--directory",str(root/"dashboard")])
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch()
            page=browser.new_page(viewport={"width":1440,"height":900})
            errors=[]
            page.on("pageerror",lambda error:errors.append(str(error)))
            page.goto("http://127.0.0.1:8765/")
            expect(page.locator("#play")).to_be_enabled()
            expect(page.locator("#metrics .metric")).to_have_count(5)
            expect(page.locator("#densityEvidence section")).to_have_count(3)
            expect(page.locator("#experimentEvidence")).to_contain_text("Adaptive complete fleet success: 88/112")
            expect(page.locator("#experimentEvidence")).to_contain_text("Control complete fleet success: 2/88")
            expect(page.locator("#experimentEvidence")).to_contain_text("Native inference: unavailable")
            expect(page.locator("#numericEvidence")).to_contain_text("Native chance to win: 100.00%")
            expect(page.locator("#numericEvidence")).to_contain_text("Relative lift: +45.02%")
            expect(page.locator("#numericEvidence svg")).to_have_count(1)
            expect(page.locator("#seed option")).to_have_count(6)
            page.locator("#seed").select_option("2")
            expect(page.locator("#tickLabel")).to_have_text("1")
            page.locator("#speed").select_option("90")
            page.locator("#play").click()
            expect(page.locator("#tickLabel")).not_to_have_text("1")
            page.locator("#reset").click()
            expect(page.locator("#tickLabel")).to_have_text("1")
            page.locator("#tick").press("End")
            assert int(page.locator("#tickLabel").inner_text())>1
            page.locator("#rolloutMode").select_option("fault")
            expect(page.locator("#rolloutAudit")).to_contain_text("ROLLBACK")
            expect(page.locator("#rolloutSummary")).to_contain_text("Final candidate allocation 0%")
            page.locator("#rolloutMode").select_option("normal")
            expect(page.locator("#rolloutAudit")).to_contain_text("ADVANCE_REHEARSAL")
            expect(page.locator("#error")).to_be_empty()
            assert page.locator("#a").evaluate("(c)=>c.getContext('2d').getImageData(0,0,c.width,c.height).data.some(v=>v!==0)")
            page.set_viewport_size({"width":390,"height":844})
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            assert not errors,errors
            browser.close()
    finally:
        server.terminate()
        server.wait(timeout=10)
if __name__=="__main__":
    main()
