import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import readline from 'readline';

const OUTPUT_DIR = 'C:\\Users\\SBS\\.gmail-mcp';
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'gcp-oauth.keys.json');

function waitForEnter(msg) {
  return new Promise(resolve => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    rl.question(msg, () => { rl.close(); resolve(); });
  });
}

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function clickIfVisible(page, selectors, timeout = 6000) {
  for (const sel of selectors) {
    try {
      const el = page.locator(sel).first();
      await el.waitFor({ state: 'visible', timeout });
      await el.click();
      return true;
    } catch {}
  }
  return false;
}

(async () => {
  console.log('브라우저를 시작합니다...\n');

  const browser = await chromium.launch({ headless: false, args: ['--start-maximized'] });
  const context = await browser.newContext({ viewport: null });
  const page = await context.newPage();

  // ── Google 로그인 ─────────────────────────────────────────
  await page.goto('https://accounts.google.com');
  await sleep(2000);

  if (page.url().includes('accounts.google.com/signin') || page.url().includes('accounts.google.com/v3')) {
    console.log('>>> Google 계정으로 로그인하세요 (gimseongjo110@gmail.com)');
    console.log('>>> 로그인 완료 후 Enter를 누르세요...');
    await waitForEnter('Enter: ');
  } else {
    console.log('로그인 상태 확인됨, 계속 진행합니다.');
  }

  // ── 1. 프로젝트 생성 ──────────────────────────────────────
  const projectName = 'gmail-mcp-' + Date.now().toString().slice(-6);
  console.log(`\n[1/4] 새 프로젝트 생성: ${projectName}`);
  await page.goto('https://console.cloud.google.com/projectcreate');
  await sleep(4000);

  try {
    await page.waitForSelector('input[id="p-name"]', { timeout: 20000 });
    await page.fill('input[id="p-name"]', '');
    await page.fill('input[id="p-name"]', projectName);
    await sleep(1500);
    const created = await clickIfVisible(page, ['button:has-text("CREATE")', 'button:has-text("만들기")']);
    if (created) {
      console.log('   생성 완료 대기 중 (10초)...');
      await sleep(10000);
    }
  } catch (e) {
    console.log('   ⚠ 자동화 실패 — 프로젝트 선택/생성 후 Enter');
    await waitForEnter('   Enter: ');
  }

  // ── 2. Gmail API 활성화 ───────────────────────────────────
  console.log('\n[2/4] Gmail API 활성화...');
  await page.goto('https://console.cloud.google.com/apis/library/gmail.googleapis.com');
  await sleep(4000);
  const apiEnabled = await clickIfVisible(page, [
    'button:has-text("ENABLE")', 'button:has-text("사용")', 'button:has-text("사용 설정")'
  ]);
  if (apiEnabled) { console.log('   활성화 완료'); await sleep(3000); }
  else { console.log('   이미 활성화되어 있거나 수동 확인 필요'); await waitForEnter('   확인 후 Enter: '); }

  // ── 3. OAuth 동의 화면 ────────────────────────────────────
  console.log('\n[3/4] OAuth 동의 화면 구성...');
  await page.goto('https://console.cloud.google.com/apis/credentials/consent');
  await sleep(4000);

  try {
    await clickIfVisible(page, ['input[value="EXTERNAL"]', 'label:has-text("External")', 'label:has-text("외부")']);
    await sleep(500);
    await clickIfVisible(page, ['button:has-text("CREATE")', 'button:has-text("만들기")']);
    await sleep(3000);

    await page.fill('input[formcontrolname="displayName"]', 'Gmail MCP').catch(() => {});
    await sleep(300);

    const emailInputs = await page.locator('input[type="email"]').all();
    for (const input of emailInputs) {
      if (await input.isVisible().catch(() => false))
        await input.fill('gimseongjo110@gmail.com').catch(() => {});
    }
    await sleep(500);

    // 저장 후 계속 3단계 반복
    for (let i = 0; i < 3; i++) {
      await clickIfVisible(page, ['button:has-text("SAVE AND CONTINUE")', 'button:has-text("저장 후 계속")']);
      await sleep(2500);
    }

    // 테스트 사용자
    await clickIfVisible(page, ['button:has-text("ADD USERS")', 'button:has-text("사용자 추가")']).catch(() => {});
    await sleep(800);
    await page.fill('input[type="email"]', 'gimseongjo110@gmail.com').catch(() => {});
    await sleep(400);
    await clickIfVisible(page, ['button:has-text("ADD")', 'button:has-text("추가")']).catch(() => {});
    await sleep(400);
    await clickIfVisible(page, ['button:has-text("SAVE AND CONTINUE")', 'button:has-text("저장 후 계속")']).catch(() => {});
    await sleep(2000);
    console.log('   동의 화면 구성 완료');
  } catch (e) {
    console.log('   ⚠ 수동 완료 후 Enter'); await waitForEnter('   Enter: ');
  }

  // ── 4. OAuth 자격증명 생성 및 JSON 다운로드 ──────────────
  console.log('\n[4/4] OAuth 2.0 자격증명 생성...');
  await page.goto('https://console.cloud.google.com/apis/credentials');
  await sleep(4000);

  try {
    await clickIfVisible(page, ['button:has-text("CREATE CREDENTIALS")', 'button:has-text("사용자 인증 정보 만들기")']);
    await sleep(1500);
    await clickIfVisible(page, ['text=OAuth client ID', 'text=OAuth 2.0 클라이언트 ID', '[data-value="oauth_client"]']);
    await sleep(2500);

    // 데스크톱 앱 선택
    await clickIfVisible(page, ['mat-select', '[role="combobox"]']);
    await sleep(700);
    await clickIfVisible(page, ['mat-option:has-text("Desktop")', 'mat-option:has-text("데스크톱")']);
    await sleep(700);

    await clickIfVisible(page, ['button:has-text("CREATE")', 'button:has-text("만들기")']);
    await sleep(3000);

    // 다운로드
    if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    const downloadPromise = page.waitForEvent('download', { timeout: 15000 });
    await clickIfVisible(page, ['button:has-text("DOWNLOAD JSON")', 'a:has-text("DOWNLOAD JSON")', 'button:has-text("JSON 다운로드")']);
    const download = await downloadPromise;
    await download.saveAs(OUTPUT_FILE);
    console.log(`\n✅ 파일 저장 완료: ${OUTPUT_FILE}`);
    await clickIfVisible(page, ['button:has-text("OK")', 'button:has-text("확인")']).catch(() => {});
  } catch (e) {
    console.log('\n   ⚠ 자동 다운로드 실패:', e.message);
    console.log(`   수동으로 JSON을 다운로드하여 저장: ${OUTPUT_FILE}`);
    await waitForEnter('   저장 완료 후 Enter: ');
  }

  await browser.close();

  if (fs.existsSync(OUTPUT_FILE)) {
    console.log('\n✅ gcp-oauth.keys.json 확인 완료!');
    console.log('다음 단계: Gmail OAuth 인증 실행\n');
  } else {
    console.error('❌ 파일 없음. 직접 배치 후 재시도하세요.'); process.exit(1);
  }
})();
