import { ref, reactive, mergeProps, unref, useSSRContext } from "vue";
import { ssrRenderAttrs, ssrRenderList, ssrRenderClass, ssrInterpolate, ssrRenderAttr, ssrIncludeBooleanAttr } from "vue/server-renderer";
import "C:/Users/-/Desktop/Hava-Durumu-Sistemi/frontend/node_modules/hookable/dist/index.mjs";
import { _ as _export_sfc } from "../server.mjs";
import "ofetch";
import "#internal/nuxt/paths";
import "C:/Users/-/Desktop/Hava-Durumu-Sistemi/frontend/node_modules/unctx/dist/index.mjs";
import "C:/Users/-/Desktop/Hava-Durumu-Sistemi/frontend/node_modules/h3/dist/index.mjs";
import "vue-router";
import "C:/Users/-/Desktop/Hava-Durumu-Sistemi/frontend/node_modules/radix3/dist/index.mjs";
import "C:/Users/-/Desktop/Hava-Durumu-Sistemi/frontend/node_modules/defu/dist/defu.mjs";
import "C:/Users/-/Desktop/Hava-Durumu-Sistemi/frontend/node_modules/ufo/dist/index.mjs";
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
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "page" }, _attrs))} data-v-1b359a6e><div class="map-container" data-v-1b359a6e><div id="map" data-v-1b359a6e></div><button class="locate-btn-overlay" title="Mevcut konumumu bul" data-v-1b359a6e><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" data-v-1b359a6e><circle cx="12" cy="12" r="3" data-v-1b359a6e></circle><path d="M12 1v4m0 14v4M1 12h4m14 0h4" data-v-1b359a6e></path></svg></button></div><div class="chat-panel" data-v-1b359a6e><div class="chat-header" data-v-1b359a6e><div class="header-info" data-v-1b359a6e><h2 class="panel-title" data-v-1b359a6e>COSMOSTORM</h2><div class="status-indicator active" data-v-1b359a6e></div></div><div class="panel-subtitle" data-v-1b359a6e>Weather Intelligence</div></div><div class="chat-messages" data-v-1b359a6e><!--[-->`);
      ssrRenderList(unref(chatMessages), (message) => {
        _push(`<div class="${ssrRenderClass([message.type, "message"])}" data-v-1b359a6e><div class="message-content" data-v-1b359a6e>${message.text ?? ""}</div><div class="message-time" data-v-1b359a6e>${ssrInterpolate(message.time)}</div></div>`);
      });
      _push(`<!--]--></div><div class="chat-input" data-v-1b359a6e><input${ssrRenderAttr("value", unref(chatInput))}${ssrRenderAttr("placeholder", unref(chatStep) === "city" ? "Hangi şehir? (örn: İstanbul, Diyarbakır, Paris)" : `${unref(selectedCity)?.name || unref(selectedCity)?.city} için ne öğrenmek istiyorsunuz? (örn: bugün hava, haftalık tahmin, yarın yağmur var mı)`)}${ssrIncludeBooleanAttr(unref(isSearching)) ? " disabled" : ""} class="input-field" data-v-1b359a6e><button${ssrIncludeBooleanAttr(unref(isSearching) || !unref(chatInput).trim()) ? " disabled" : ""} class="send-btn" data-v-1b359a6e><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" data-v-1b359a6e><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" data-v-1b359a6e></path></svg></button></div></div></div>`);
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
export {
  index as default
};
//# sourceMappingURL=index-DEcUAp6j.js.map
