"""Chromium interaction test for real native pose replay."""
import subprocess,sys
from playwright.sync_api import sync_playwright,expect

def main():
    server=subprocess.Popen([sys.executable,"-m","http.server","8765","--bind","127.0.0.1","--directory","dashboard"])
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch()
            page=browser.new_page(viewport={"width":1440,"height":900})
            errors=[]
            page.on("pageerror",lambda e:errors.append(str(e)))
            page.goto("http://127.0.0.1:8765/physics.html")
            expect(page.locator("#physicalPlay")).to_be_enabled(timeout=30000)
            expect(page.locator("#fleetSize option")).to_have_count(3)
            expect(page.locator("#physicalEvidence")).to_contain_text("V5 fixed reversal penalty")
            canvas=page.locator("#leftScene")
            before=canvas.evaluate("(c)=>c.toDataURL()")
            page.locator("#physicalPlay").click()
            expect(page.locator("#physicalClock")).not_to_have_text("0.0 s")
            page.locator("#physicalPlay").click()
            assert canvas.evaluate("(c)=>c.toDataURL()")!=before
            page.locator("#physicalReset").click()
            expect(page.locator("#physicalClock")).to_have_text("0.0 s")
            page.locator("#topView").click()
            assert canvas.evaluate("(c)=>c.toDataURL()")!=before
            page.locator("#orbitView").click()
            page.locator("#fleetSize").select_option("2")
            expect(page.locator("#leftCount")).to_have_text("0/24 complete")
            page.locator("#physicalTime").press("End")
            expect(page.locator("#rightCount")).to_have_text("24/24 complete")
            page.screenshot(path="physical-preview.png",full_page=True)
            page.set_viewport_size({"width":390,"height":844})
            assert page.evaluate("document.documentElement.scrollWidth<=innerWidth")
            expect(page.locator("#physicalError")).to_be_empty()
            assert not errors,errors
            browser.close()
    finally:
        server.terminate();server.wait(timeout=10)
if __name__=="__main__":main()
