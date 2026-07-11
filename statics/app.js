/* Advance Report Studio 前端逻辑（Vue 3，无构建链） */
'use strict';

const OPT = {
  gasTypes: ["Cooktops/hobs", "Duct Heating", "Hot Water Service"],
  locations: ["Bedroom", "Hallway", "Kitchen", "Living room", "Other"],
  manufacturers: ["ASKO", "Bosch", "Chef", "Delonghi", "Electrolux", "Fisher & Paykel", "GE",
    "Haier", "ILVE", "LG", "Miele", "Omega", "Samsung", "Smeg", "Westinghouse", "Whirlpool"],
  flues: ["N/A"],
  brands: ["ANKA", "Clipsal", "Ionization", "Legrand", "Lifesaver", "Matelec",
    "Photoelectric", "Quell", "Tesla", "Trafalgar"],
  pfn: ["Pass", "Fail", "N/A"],
  ynn: ["Yes", "No", "N/A"],
  mainsTypes: ["Cable", "Copper"],
  earthTypes: ["Cable", "Copper", "Other"],
  supplyTypes: ["Underground", "Overhead"],
  mainsSizes: ["16mm", "25mm"],
};

const OVERALL_SPECS = [
  { label: "Compliant / Non-Compliant", options: ["Compliant", "Non-Compliant"] },
  { label: "Recommendation", options: ["N/A", "Yes"] },
  { label: "Faulty Found", options: ["N/A", "Yes"] },
  { label: "Safety Issue", options: ["N/A", "Yes"] },
  { label: "Disconnected\n(Urgent Repair)", options: ["N/A", "Yes"] },
];

const INSTALLATION_ITEMS = [
  { order: 1, label: "APPLIANCES TESTED:", description: "Are all appliances certified and installed in accordance with AS/NZS5601?" },
  { order: 2, label: "SUPPLY PIPEWORK VISUAL:", description: "Are the appliances and its components accessible for service and adjustment?" },
  { order: 3, label: "INSTALLATION PIPEWORK VISUAL:", description: "All pipework and valves fitted as required by AS/NZS5601?" },
  { order: 4, label: "GAS LINE TEST:", description: "Is the property gastight in accordance with AS/NZS5601?" },
  { order: 5, label: "METER ACCESS:", description: "Did the Gas Meter have acceptable access as per AS/NZS5601?" },
  { order: 6, label: "APPLIANCES OPERATION:", description: "Are all appliances operating as per manufacturers operating instructions?" },
  { order: 7, label: "APPLIANCE CLEARANCES:", description: "Do all Appliance Clearances comply with AS/NZS5601?" },
  { order: 8, label: "DEFECTS FOUND:", description: "Were there any defects found at the property?" },
];

const DEFAULT_COMPANY = { name: "Advance Essential Services", address: "Unit 56/31 Norcal Rd, Nunawading" };

const ELEC_FITTINGS = [
  { key: "socketOutlets", label: "Socket Outlets" },
  { key: "extractFans", label: "Extract Fans" },
  { key: "switches", label: "Switches" },
  { key: "wetAreasIp", label: "Wet Areas IP Rating" },
  { key: "indoorLighting", label: "Indoor Lighting" },
  { key: "exteriorLighting", label: "Exterior Lighting" },
  { key: "hotWater", label: "Hot Water" },
  { key: "heating", label: "Heating" },
  { key: "rangehood", label: "Rangehood" },
  { key: "oven", label: "Oven" },
];

const uid = () => Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
const wrap = (value, label = "", options = []) => ({ value: value || "", label, options });
const dateOnly = s => (typeof s === "string" && s.length >= 10 && /^\d{4}-\d{2}-\d{2}/.test(s)) ? s.slice(0, 10) : "";

/* ------------------------- 内部模型构造 ------------------------- */

function newBase(type) {
  return {
    agentName: "", branchAddress: "", referenceId: "", rentalType: "Rental Property",
    propertyAddress: "", inspectedDate: "", nextCheckDue: "",
    inspectorName: "", inspectorLicence: "",
    buildingClass: type === "smoke" ? "Class 1a" : "",
    premisesDescription: type === "electrical" ? "Domestic" : "",
    companyName: DEFAULT_COMPANY.name, companyAddress: DEFAULT_COMPANY.address,
  };
}

function newElectrical(id) {
  return {
    id, type: "electrical", base: newBase("electrical"),
    overall: OVERALL_SPECS.map(s => ({ ...s, ticked: s.options[0], remark: "" })),
    mains: { type: "Cable", supply: "Underground", size: "16mm", entryCondition: "Pass", cableCondition: "Pass", switchType: "" },
    mainEarth: { type: "Cable", size: "16mm", connectionCondition: "Pass", resistanceTest: "Pass", location: "" },
    switchboard: { rcdInstalled: "Pass", earthBar: "Pass", fusesLabelled: "Pass", menLink: "Pass", rcdTripTest: "Pass", ipFireRating: "Pass", polarityTest: "Pass", overallCondition: "Pass", subCircuitEarthTest: "Pass", location: "" },
    distributionBoard: { present: "", submainCondition: "", fusesLabelled: "", earthBar: "", mcbCount: "", circuitsLabelled: "", fusesCount: "", overallCondition: "", rcdCount: "", location: "" },
    finalCircuits: { cableType: "", bareEarthsSleeved: "", insulationCondition: "Pass", rewiringRequired: "No", cablesSupported: "Pass", circuitsToRewire: "" },
    fittings: { socketOutlets: "Pass", extractFans: "Pass", switches: "Pass", wetAreasIp: "Pass", indoorLighting: "Pass", exteriorLighting: "Pass", hotWater: "Pass", heating: "Pass", rangehood: "Pass", oven: "Pass", otherFittings: "", garageShed: "" },
    urgentRepairs: "", observations: "",
    photoBlocks: [newPhotoBlock()],
  };
}

function newGas(id) {
  return {
    id, type: "gas", base: newBase("gas"),
    overall: OVERALL_SPECS.map(s => ({ ...s, ticked: s.options[0], remark: "" })),
    appliances: [newApplianceRow()],
    service: [newServiceRow()],
    installation: INSTALLATION_ITEMS.map(i => ({ ...i, value: "Pass" })),
    photoBlocks: [newPhotoBlock()],
    carbon: { fitted: "", test: "", tested: "" },
  };
}

function newSmoke(id) {
  return {
    id, type: "smoke", base: newBase("smoke"),
    metCurrent: true, metNew: true, overallCompliant: "Compliant",
    alarms: [newAlarm(), newAlarm(), newAlarm()],
  };
}

function newApplianceRow() {
  return { type: "", location: "", manufacturer: "", modelNo: "N/A", serialNo: "N/A", flueType: "N/A", installation: "Compliant" };
}
function newServiceRow() {
  return { kpa: "", ventilation: "Pass", flueVisual: "Pass", flueOperation: "Pass", carbonMonoxideTest: "Pass", safeToUse: "Yes" };
}
function newPhotoBlock() {
  return { slotId: uid(), title: "", status: "Compliant", remark: "", photoUrl: "" };
}
function newAlarm() {
  return { slotId: uid(), status: "Compliant", brand: "", location: "", expiry: "", photoUrl: "" };
}

/* ------------------------- 模型 <-> 后端 JSON ------------------------- */

function toBackend(rpt) {
  const b = rpt.base;
  const baseInfo = {
    type: rpt.type === "smoke" ? "Smoke" : "Gas",
    clientBranch: { agentName: b.agentName, branchAddress: b.branchAddress },
    referenceId: b.referenceId,
    rentalType: b.rentalType,
    propertyAddress: b.propertyAddress,
    inspectedDate: b.inspectedDate,
    nextCheckDue: b.nextCheckDue,
    inspector: { id: "1", name: b.inspectorName, licenceNo: b.inspectorLicence },
  };
  if (rpt.type === "electrical") {
    baseInfo.premisesDescription = b.premisesDescription;
    baseInfo.company = { name: b.companyName, address: b.companyAddress };
    return {
      baseInfo,
      elecCheckDetails: {
        overallFindings: rpt.overall.map(f => ({
          label: f.label, options: f.options, tickedPos: f.ticked, remark: f.remark,
        })),
        mains: { ...rpt.mains },
        mainEarth: { ...rpt.mainEarth },
        switchboard: { ...rpt.switchboard },
        distributionBoard: { ...rpt.distributionBoard },
        finalCircuits: { ...rpt.finalCircuits },
        fittings: { ...rpt.fittings },
        urgentRepairs: rpt.urgentRepairs,
        observations: rpt.observations,
        applianceReport: rpt.photoBlocks
          .filter(p => p.title || p.photoUrl)
          .map(p => ({ title: p.title, status: p.status, photoUrl: p.photoUrl })),
      },
    };
  }
  if (rpt.type === "smoke") {
    baseInfo.buildingClass = b.buildingClass;
    baseInfo.company = { name: b.companyName, address: b.companyAddress };
    return {
      baseInfo,
      smokeCheckDetails: {
        metCurrentRequirements: !!rpt.metCurrent,
        metNewRequirements: !!rpt.metNew,
        overallCompliant: rpt.overallCompliant,
        alarms: rpt.alarms.map(a => ({
          status: a.status, brand: a.brand, location: a.location,
          expiry: a.expiry, photoUrl: a.photoUrl,
        })),
      },
    };
  }
  return {
    baseInfo,
    gasCheckDetails: {
      overallFindings: rpt.overall.map(f => ({
        label: f.label, options: f.options, tickedPos: f.ticked, remark: f.remark,
      })),
      applianceDetails: rpt.appliances.map(a => ({
        type: wrap(a.type, "TYPE", OPT.gasTypes),
        location: wrap(a.location, "LOCATION", OPT.locations),
        manufacturer: wrap(a.manufacturer, "MANUFACTURER", OPT.manufacturers),
        modelNo: wrap(a.modelNo, "MODEL NO."),
        serialNo: wrap(a.serialNo, "SERIAL NO."),
        flueType: wrap(a.flueType, "FLUE TYPE", OPT.flues),
        installation: wrap(a.installation, "INSTALLATION", ["Compliant", "Non-Compliant"]),
      })),
      serviceAndInspection: rpt.service.map(s => ({
        operatingPressure: wrap(s.kpa, "OPERATING PRESSURE\n(KPA)"),
        ventilation: wrap(s.ventilation, "VENTILATION", OPT.pfn),
        flueVisual: wrap(s.flueVisual, "FLUE VISUAL", OPT.pfn),
        flueOperation: wrap(s.flueOperation, "FLUE OPERATION", OPT.pfn),
        carbonMonoxideTest: wrap(s.carbonMonoxideTest, "CARBON MONOXIDE TEST", OPT.pfn),
        safeToUse: wrap(s.safeToUse, " SAFE TO USE", OPT.ynn),
      })),
      installationDetails: rpt.installation.map(i => ({
        order: i.order, description: i.description,
        result: { value: i.value, label: i.label, options: ["Pass", "Fail"] },
      })),
      gasApplianceReport: rpt.photoBlocks
        .filter(p => p.title || p.photoUrl || p.remark)
        .map(p => ({
          type: {
            value: p.title, label: "", "radio-value": p.status,
            options: [{ name: p.title, radio: ["Compliant", "Non-Compliant"] }],
          },
          remark: p.remark,
          photoUrl: p.photoUrl ? [p.photoUrl] : [],
        })),
      carbonAlarmDetails: {
        approvedAlarmFitted: rpt.carbon.fitted,
        alarmTest: rpt.carbon.test,
        noAppliancesTested: rpt.carbon.tested,
      },
    },
  };
}

function fromBackend(id, data) {
  const bi = data.baseInfo || {};
  const t = (bi.type || "gas").toLowerCase();
  const type = t.startsWith("smoke") ? "smoke" : (t === "electrical" ? "electrical" : "gas");
  const rpt = type === "smoke" ? newSmoke(id) : (type === "electrical" ? newElectrical(id) : newGas(id));
  const cb = bi.clientBranch || {};
  const insp = bi.inspector || {};
  const comp = bi.company || {};
  Object.assign(rpt.base, {
    agentName: cb.agentName || "", branchAddress: cb.branchAddress || "",
    referenceId: bi.referenceId || "", rentalType: bi.rentalType || "Rental Property",
    propertyAddress: bi.propertyAddress || "",
    inspectedDate: dateOnly(bi.inspectedDate), nextCheckDue: dateOnly(bi.nextCheckDue),
    inspectorName: insp.name || "", inspectorLicence: insp.licenceNo || "",
    buildingClass: bi.buildingClass || rpt.base.buildingClass,
    premisesDescription: bi.premisesDescription || rpt.base.premisesDescription,
    companyName: comp.name || DEFAULT_COMPANY.name,
    companyAddress: comp.address || DEFAULT_COMPANY.address,
  });

  if (type === "electrical") {
    const d = data.elecCheckDetails || {};
    const findings = d.overallFindings || [];
    rpt.overall = OVERALL_SPECS.map((spec, i) => {
      const f = findings[i] || {};
      return { ...spec, ticked: f.tickedPos || spec.options[0], remark: f.remark || "" };
    });
    ["mains", "mainEarth", "switchboard", "distributionBoard", "finalCircuits", "fittings"]
      .forEach(k => { Object.assign(rpt[k], d[k] || {}); });
    rpt.urgentRepairs = d.urgentRepairs || "";
    rpt.observations = d.observations || "";
    rpt.photoBlocks = (d.applianceReport || []).map(p => ({
      slotId: uid(), title: p.title || "", status: p.status || "Compliant",
      remark: "", photoUrl: p.photoUrl || "",
    }));
    if (!rpt.photoBlocks.length) rpt.photoBlocks = [newPhotoBlock()];
    return rpt;
  }

  if (type === "smoke") {
    const d = data.smokeCheckDetails || {};
    rpt.metCurrent = !!d.metCurrentRequirements;
    rpt.metNew = !!d.metNewRequirements;
    rpt.overallCompliant = d.overallCompliant || "Compliant";
    rpt.alarms = (d.alarms || []).map(a => ({
      slotId: uid(), status: a.status || "Compliant", brand: a.brand || "",
      location: a.location || "", expiry: a.expiry || "", photoUrl: a.photoUrl || "",
    }));
    if (!rpt.alarms.length) rpt.alarms = [newAlarm()];
    return rpt;
  }

  const d = data.gasCheckDetails || {};
  const findings = d.overallFindings || [];
  rpt.overall = OVERALL_SPECS.map((spec, i) => {
    const f = findings[i] || {};
    return { ...spec, ticked: f.tickedPos || spec.options[0], remark: f.remark || "" };
  });
  rpt.appliances = (d.applianceDetails || []).map(a => ({
    type: a.type?.value || "", location: a.location?.value || "",
    manufacturer: a.manufacturer?.value || "", modelNo: a.modelNo?.value || "",
    serialNo: a.serialNo?.value || "", flueType: a.flueType?.value || "",
    installation: a.installation?.value || "",
  }));
  if (!rpt.appliances.length) rpt.appliances = [newApplianceRow()];
  rpt.service = (d.serviceAndInspection || []).map(s => ({
    kpa: s.operatingPressure?.value || "", ventilation: s.ventilation?.value || "",
    flueVisual: s.flueVisual?.value || "", flueOperation: s.flueOperation?.value || "",
    carbonMonoxideTest: s.carbonMonoxideTest?.value || "", safeToUse: s.safeToUse?.value || "",
  }));
  if (!rpt.service.length) rpt.service = [newServiceRow()];
  const insMap = {};
  (d.installationDetails || []).forEach(i => { insMap[i.order] = i.result?.value; });
  rpt.installation = INSTALLATION_ITEMS.map(i => ({ ...i, value: insMap[i.order] || "Pass" }));
  rpt.photoBlocks = (d.gasApplianceReport || []).map(p => ({
    slotId: uid(), title: p.type?.value || "", status: p.type?.["radio-value"] || "Compliant",
    remark: p.remark || "", photoUrl: (p.photoUrl || [])[0] || "",
  }));
  if (!rpt.photoBlocks.length) rpt.photoBlocks = [newPhotoBlock()];
  const carbon = d.carbonAlarmDetails || {};
  rpt.carbon = {
    fitted: carbon.approvedAlarmFitted || "", test: carbon.alarmTest || "",
    tested: carbon.noAppliancesTested || "",
  };
  return rpt;
}

/* ------------------------- API ------------------------- */

async function api(path, opts = {}) {
  const resp = await fetch(path, opts);
  const body = await resp.json();
  if (!body.success) throw new Error(body.msg || "Request failed");
  return body.data;
}

/* ------------------------- Vue App ------------------------- */

const { createApp } = Vue;

createApp({
  data() {
    return {
      view: "home", reports: [], rpt: null, stepIdx: 0,
      previewUrl: "", busy: false, toast: "", toastType: "", imgBust: Date.now(),
      OPT, ELEC_FITTINGS,
    };
  },
  computed: {
    steps() {
      if (!this.rpt) return [];
      if (this.rpt.type === "smoke") return ["Basic Info", "Declarations", "Smoke Alarms"];
      if (this.rpt.type === "electrical")
        return ["Basic Info", "Overall Findings", "Safety Services", "Fittings & Notes", "Photo Report"];
      return ["Basic Info", "Overall Findings", "Appliances", "Service & Inspection", "Installation", "Photo Report"];
    },
    curStep() { return this.steps[this.stepIdx] || ""; },
  },
  mounted() { this.loadReports(); },
  methods: {
    say(msg, isErr = false) {
      this.toast = msg; this.toastType = isErr ? "err" : "";
      clearTimeout(this._t);
      this._t = setTimeout(() => { this.toast = ""; }, isErr ? 5000 : 2500);
    },
    fmtTime(s) { return (s || "").replace("T", " ").slice(0, 16); },
    imgSrc(url) { return url ? `${url}?t=${this.imgBust}` : ""; },
    goHome() { this.view = "home"; this.loadReports(); },

    async loadReports() {
      try { this.reports = await api("/api/reports/"); }
      catch (e) { this.say("Failed to load reports: " + e.message, true); }
    },
    newReport(type) {
      this.rpt = type === "smoke" ? newSmoke(uid())
        : (type === "electrical" ? newElectrical(uid()) : newGas(uid()));
      this.stepIdx = 0;
      this.view = "edit";
    },
    async openReport(id) {
      this.busy = true;
      try {
        const detail = await api(`/api/reports/${id}/`);
        this.rpt = fromBackend(id, detail.data || {});
        this.stepIdx = 0;
        this.view = "edit";
      } catch (e) { this.say(e.message, true); }
      finally { this.busy = false; }
    },
    async delReport(id) {
      if (!confirm("Delete this report?")) return;
      try {
        await api(`/api/reports/${id}/`, { method: "DELETE" });
        this.loadReports();
      } catch (e) { this.say(e.message, true); }
    },
    async saveDraft() {
      this.busy = true;
      try {
        await api("/api/reports/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id: this.rpt.id, data: toBackend(this.rpt) }),
        });
        this.say("✅ Draft saved");
      } catch (e) { this.say("Save failed: " + e.message, true); }
      finally { this.busy = false; }
    },

    addAppliance() { this.rpt.appliances.push(newApplianceRow()); },
    addService() { this.rpt.service.push(newServiceRow()); },
    addPhotoBlock() { this.rpt.photoBlocks.push(newPhotoBlock()); },
    addAlarm() { this.rpt.alarms.push(newAlarm()); },

    async uploadPhoto(event, target) {
      const file = event.target.files[0];
      event.target.value = "";
      if (!file) return;
      this.busy = true;
      try {
        const fd = new FormData();
        fd.append("file", file);
        fd.append("key", `${this.rpt.id}/${target.slotId}`);
        target.photoUrl = await api("/api/photos/", { method: "POST", body: fd });
        this.imgBust = Date.now();  // 覆盖上传后强制刷新缩略图
        this.say("📷 Photo uploaded");
      } catch (e) { this.say("Upload failed: " + e.message, true); }
      finally { this.busy = false; }
    },

    async doPreview() {
      this.busy = true;
      try {
        const resp = await fetch("/api/generate/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id: this.rpt.id, data: toBackend(this.rpt), mode: "preview" }),
        });
        if (!resp.ok || !(resp.headers.get("Content-Type") || "").includes("pdf")) {
          const body = await resp.json().catch(() => ({}));
          throw new Error(body.msg || `Generation failed (${resp.status})`);
        }
        const blob = await resp.blob();
        if (this.previewUrl) URL.revokeObjectURL(this.previewUrl);
        this.previewUrl = URL.createObjectURL(blob);
        this.view = "preview";
      } catch (e) { this.say("Preview failed: " + e.message, true); }
      finally { this.busy = false; }
    },

    async doDownload() {
      this.busy = true;
      try {
        const res = await api("/api/generate/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id: this.rpt.id, data: toBackend(this.rpt), mode: "final" }),
        });
        const a = document.createElement("a");
        a.href = res.url;
        a.download = res.url.split("/").pop();
        document.body.appendChild(a);
        a.click();
        a.remove();
        this.say("✅ PDF generated, download started");
        this.loadReports();
      } catch (e) { this.say("Generation failed: " + e.message, true); }
      finally { this.busy = false; }
    },

    async importPdf(event) {
      const file = event.target.files[0];
      event.target.value = "";
      if (!file) return;
      this.busy = true;
      try {
        const fd = new FormData();
        fd.append("file", file);
        const res = await api("/api/parse-pdf/", { method: "POST", body: fd });
        this.rpt = fromBackend(uid(), res.data);
        this.stepIdx = 0;
        this.view = "edit";
        this.say(res.source === "embedded"
          ? "✅ Restored from data embedded in the PDF"
          : "✅ Parsed PDF form fields — please review before exporting");
      } catch (e) { this.say("Import failed: " + e.message, true); }
      finally { this.busy = false; }
    },
  },
}).mount("#app");
