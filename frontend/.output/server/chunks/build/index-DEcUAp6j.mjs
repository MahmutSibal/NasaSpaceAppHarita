import { ref, reactive, mergeProps, unref, useSSRContext } from 'vue';
import { ssrRenderAttrs, ssrRenderList, ssrRenderClass, ssrInterpolate, ssrRenderAttr, ssrIncludeBooleanAttr } from 'vue/server-renderer';
import { _ as _export_sfc } from './server.mjs';
import '../_/nitro.mjs';
import 'node:http';
import 'node:https';
import 'node:events';
import 'node:buffer';
import 'node:fs';
import 'node:path';
import 'node:crypto';
import 'node:url';
import '../routes/renderer.mjs';
import 'vue-bundle-renderer/runtime';
import 'unhead/server';
import 'devalue';
import 'unhead/utils';
import 'unhead/plugins';
import 'vue-router';

const _sfc_main = {
  __name: "index",
  __ssrInlineRender: true,
  setup(__props) {
    ref(null);
    ref(null);
    const chatInput = ref("");
    const chatMessages = ref([]);
    const isSearching = ref(false);
    const chatStep = ref("city");
    const selectedCity = ref(null);
    ref(true);
    ref(null);
    ref(0);
    reactive({ lat: 0, lng: 0 });
    ref([]);
    return (_ctx, _push, _parent, _attrs) => {
      var _a, _b;
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "page" }, _attrs))} data-v-1b359a6e><div class="map-container" data-v-1b359a6e><div id="map" data-v-1b359a6e></div><button class="locate-btn-overlay" title="Mevcut konumumu bul" data-v-1b359a6e><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" data-v-1b359a6e><circle cx="12" cy="12" r="3" data-v-1b359a6e></circle><path d="M12 1v4m0 14v4M1 12h4m14 0h4" data-v-1b359a6e></path></svg></button></div><div class="chat-panel" data-v-1b359a6e><div class="chat-header" data-v-1b359a6e><div class="header-info" data-v-1b359a6e><h2 class="panel-title" data-v-1b359a6e>COSMOSTORM</h2><div class="status-indicator active" data-v-1b359a6e></div></div><div class="panel-subtitle" data-v-1b359a6e>Weather Intelligence</div></div><div class="chat-messages" data-v-1b359a6e><!--[-->`);
      ssrRenderList(unref(chatMessages), (message) => {
        var _a2;
        _push(`<div class="${ssrRenderClass([message.type, "message"])}" data-v-1b359a6e><div class="message-content" data-v-1b359a6e>${(_a2 = message.text) != null ? _a2 : ""}</div><div class="message-time" data-v-1b359a6e>${ssrInterpolate(message.time)}</div></div>`);
      });
      _push(`<!--]--></div><div class="chat-input" data-v-1b359a6e><input${ssrRenderAttr("value", unref(chatInput))}${ssrRenderAttr("placeholder", unref(chatStep) === "city" ? "Hangi \u015Fehir? (\xF6rn: \u0130stanbul, Diyarbak\u0131r, Paris)" : `${((_a = unref(selectedCity)) == null ? void 0 : _a.name) || ((_b = unref(selectedCity)) == null ? void 0 : _b.city)} i\xE7in ne \xF6\u011Frenmek istiyorsunuz? (\xF6rn: bug\xFCn hava, haftal\u0131k tahmin, yar\u0131n ya\u011Fmur var m\u0131)`)}${ssrIncludeBooleanAttr(unref(isSearching)) ? " disabled" : ""} class="input-field" data-v-1b359a6e><button${ssrIncludeBooleanAttr(unref(isSearching) || !unref(chatInput).trim()) ? " disabled" : ""} class="send-btn" data-v-1b359a6e><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" data-v-1b359a6e><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" data-v-1b359a6e></path></svg></button></div></div></div>`);
    };
  }
};
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("pages/index.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const index = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-1b359a6e"]]);

export { index as default };
//# sourceMappingURL=index-DEcUAp6j.mjs.map
