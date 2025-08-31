import * as DocumentPicker from "expo-document-picker";
import { useState } from "react";
import { View, Text, Pressable, ActivityIndicator, ScrollView } from "react-native";

const NODE_API_BASE = process.env.EXPO_PUBLIC_NODE_API_BASE || "http://localhost:4000";

export default function Upload() {
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const pick = async () => {
    setError(null);
    const res = await DocumentPicker.getDocumentAsync({
      type: ["application/pdf", "image/*"],
      multiple: false,
      copyToCacheDirectory: true
    });
    if (res.canceled) return;

    const file = res.assets[0];
    const form = new FormData();
    form.append("file", {
      uri: file.uri,
      name: file.name || "upload",
      type: file.mimeType || "application/octet-stream"
    });

    try {
      setBusy(true);
      const r = await fetch(`${NODE_API_BASE}/ocr/extract`, {
        method: "POST",
        headers: { "Accept": "application/json" },
        body: form
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const json = await r.json();
      setResult(json);
    } catch (e) {
      setError(String(e?.message || e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <View style={{ flex: 1, padding: 16, gap: 16 }}>
      <Pressable
        onPress={pick}
        disabled={busy}
        style={{ backgroundColor: "#111827", padding: 14, borderRadius: 12, opacity: busy ? 0.6 : 1 }}
      >
        <Text style={{ color: "white", textAlign: "center", fontWeight: "600" }}>
          {busy ? "Processing..." : "Pick a PDF/Image"}
        </Text>
      </Pressable>

      {busy && <ActivityIndicator size="large" />}

      {error && (
        <Text style={{ color: "crimson" }}>Error: {error}</Text>
      )}

      {result && (
        <ScrollView style={{ flex: 1, backgroundColor: "#F3F4F6", padding: 12, borderRadius: 12 }}>
          <Text style={{ fontWeight: "700", marginBottom: 8 }}>OCR Result</Text>
          {result.blocks?.map((b, i) => (
            <Text key={i} style={{ marginBottom: 8 }}>{b.text}</Text>
          ))}
        </ScrollView>
      )}
    </View>
  );
}
