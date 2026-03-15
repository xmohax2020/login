from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from playwright.sync_api import BrowserContext, Page, sync_playwright

from publisher.config import PublisherConfig
from publisher.models import DesignRow


def fill_text_if_exists(page: Page, selector: str, value: str) -> None:
    loc = page.locator(selector)
    if loc.count() > 0:
        loc.first.fill(value)


def click_if_exists(page: Page, selector: str) -> None:
    loc = page.locator(selector)
    if loc.count() > 0:
        loc.first.click()


def upload_one_design(context: BrowserContext, config: PublisherConfig, row: DesignRow, mode: str) -> dict:
    page = context.new_page()
    try:
        page.goto(f"{config.base_url}{config.upload_path}", wait_until="domcontentloaded")

        file_input = page.locator(config.selectors["file_input"]).first
        file_input.set_input_files(str(row.file_path))

        fill_text_if_exists(page, config.selectors["title_input"], row.title)
        fill_text_if_exists(page, config.selectors["description_input"], row.description)
        fill_text_if_exists(page, config.selectors["tags_input"], row.tags)

        if row.maturity == "safe":
            click_if_exists(page, config.selectors["mature_toggle_safe"])

        if row.is_public:
            click_if_exists(page, config.selectors["public_toggle"])

        click_if_exists(page, config.selectors["save_button"])

        if mode == "publish":
            click_if_exists(page, config.selectors["publish_button"])

        return {"ok": True, "mode": mode, "design": asdict(row)}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "mode": mode, "design": asdict(row), "error": str(exc)}
    finally:
        page.close()


def run_publish(config: PublisherConfig, designs: list[DesignRow], mode: str) -> list[dict]:
    config.state_file.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=config.headless, slow_mo=config.slow_mo_ms)
        context = browser.new_context(storage_state=str(config.state_file))
        results = [upload_one_design(context, config, row, mode=mode) for row in designs]
        context.close()
        browser.close()
    return results


def save_login_state(base_url: str, state_file: Path) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=80)
        context = browser.new_context()
        page = context.new_page()
        page.goto(base_url, wait_until="domcontentloaded")
        input("سجّل الدخول يدويًا في المتصفح ثم اضغط Enter هنا...")
        context.storage_state(path=str(state_file))
        context.close()
        browser.close()
