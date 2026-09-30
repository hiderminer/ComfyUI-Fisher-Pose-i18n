// UI language for the editors. Only on-screen text lives in the dictionaries: the Chinese
// edit instructions sent to the model and values saved in workflows (modes, prompt style,
// reference choices) stay as they are.
import zh from './i18n/zh.mjs';
import ja from './i18n/ja.mjs';
import en from './i18n/en.mjs';

const DICTIONARIES = { zh, ja, en };

// ComfyUI locale codes (zh, zh-TW, ja, en, ko, ...) → one of ours; anything else falls back to English.
export function resolveLang(code) {
    const primary = String(code || '').toLowerCase().split(/[-_]/)[0];
    return DICTIONARIES[primary] ? primary : 'en';
}

const requested = typeof location === 'undefined' ? '' : new URLSearchParams(location.search).get('lang');
const browser = typeof navigator === 'undefined' ? '' : navigator.language;
export const LANG = resolveLang(requested || browser);

export function translate(lang, key, params = {}) {
    const text = DICTIONARIES[lang]?.[key] ?? en[key] ?? zh[key] ?? key;
    return text.replace(/\{(\w+)\}/g, (match, name) => (name in params ? String(params[name]) : match));
}

export const t = (key, params) => translate(LANG, key, params);

// data-i18n → textContent, data-i18n-lead → only the leading text node (keeps child
// inputs/outputs), data-i18n-html → trusted markup from our own dictionaries,
// data-i18n-<attribute> → that attribute (title, placeholder, alt, aria-label).
const ATTRIBUTES = ['title', 'placeholder', 'alt', 'aria-label'];
export function applyI18n(root = document) {
    if (root === document) {
        document.documentElement.lang = { zh: 'zh-CN', ja: 'ja', en: 'en' }[LANG];
        if (document.title && document.documentElement.dataset.i18nTitle) document.title = t(document.documentElement.dataset.i18nTitle);
    }
    for (const element of root.querySelectorAll('[data-i18n]')) element.textContent = t(element.dataset.i18n);
    for (const element of root.querySelectorAll('[data-i18n-lead]')) {
        const text = t(element.dataset.i18nLead), lead = element.firstChild;
        if (lead?.nodeType === Node.TEXT_NODE) lead.textContent = text + (lead.textContent.match(/\s+$/)?.[0] ?? '');
        else element.prepend(text);
    }
    for (const element of root.querySelectorAll('[data-i18n-html]')) element.innerHTML = t(element.dataset.i18nHtml);
    for (const attribute of ATTRIBUTES) {
        for (const element of root.querySelectorAll(`[data-i18n-${attribute}]`)) element.setAttribute(attribute, t(element.getAttribute(`data-i18n-${attribute}`)));
    }
}
