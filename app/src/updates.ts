export function mountUpdates(parent: HTMLElement, invoke: (command: string, args?: Record<string, unknown>) => Promise<any>) {
  const box=document.createElement("section");box.className="card";
  const title=document.createElement("h3");title.textContent="Private App-Updates";
  const access=document.createElement("input");access.type="password";access.autocomplete="off";access.placeholder="Repository-Lesezugang";access.setAttribute("aria-label","Repository-Lesezugang (nur für diese Prüfung)");
  const check=document.createElement("button");check.textContent="Nach Updates suchen";
  const status=document.createElement("p");status.setAttribute("role","status");status.textContent="Der Lesezugang bleibt nur im Arbeitsspeicher. Installation erst nach Signatur- und Apple-Prüfung.";
  const install=document.createElement("button");install.textContent="Update installieren";install.hidden=true;
  const label=document.createElement("label");const accepted=document.createElement("input");accepted.type="checkbox";label.append(accepted,document.createTextNode("Installation dieser Version bestätigen"));label.hidden=true;
  let version="";
  check.onclick=async()=>{check.disabled=true;install.hidden=true;label.hidden=true;accepted.checked=false;status.textContent="Wird geprüft …";const zugang=access.value;access.value="";try{const r=await invoke("update_pruefen",{zugang});if(r.zustand==="verfuegbar"){version=r.version;status.textContent="Version "+version+" verfügbar";install.hidden=false;label.hidden=false;}else status.textContent=r.zustand==="aktuell"?"Die installierte Version ist aktuell.":"Updatekanal nicht eingerichtet.";}catch(e){status.textContent=String(e);}finally{check.disabled=false;}};
  install.onclick=async()=>{if(!accepted.checked){status.textContent="Bitte die Installation ausdrücklich bestätigen.";return;}install.disabled=true;try{await invoke("update_installieren",{version,bestaetigt:true});status.textContent="Update installiert. Bitte die App neu starten.";}catch(e){status.textContent=String(e);}finally{install.disabled=false;}};
  box.append(title,access,check,status,label,install);parent.append(box);
}
