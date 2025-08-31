import { Link } from "expo-router";
import { View, Text, Pressable } from "react-native";

export default function Home() {
  return (
    <View style={{ flex: 1, padding: 24, gap: 16, justifyContent: "center" }}>
      <Text style={{ fontSize: 22, fontWeight: "600" }}>
        OkemID — OCR/NLP Demo
      </Text>
      <Link asChild href="/upload">
        <Pressable style={{ backgroundColor: "#111827", padding: 14, borderRadius: 12 }}>
          <Text style={{ color: "white", textAlign: "center", fontWeight: "600" }}>
            Upload Document for OCR
          </Text>
        </Pressable>
      </Link>
    </View>
  );
}
