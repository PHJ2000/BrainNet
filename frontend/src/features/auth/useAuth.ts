// features/auth/useAuth.ts
import { useRouter } from "next/navigation";
import { useState } from "react";
import { login, register } from "./authApi";

export const useAuth = () => {
  const router = useRouter();
  const [error, setError] = useState("");

  const handleLogin = async (email: string, password: string) => {
    try {
      const { access_token } = await login(email, password);
      localStorage.setItem("token", access_token);
      router.push("/dashboard");
    } catch {
      setError("이메일 또는 비밀번호가 올바르지 않습니다.");
    }
  };

  const handleRegister = async (email: string, password: string, name?: string) => {

    if (!email || !email.includes("@") || !password) {
    setError("이메일과 비밀번호를 올바르게 입력해주세요.");
    return;
  }

  console.log("📦 register payload:", { email, password, name }); // ← 여기

    try {
      await register(email, password, name);
      await handleLogin(email, password); // 자동 로그인
    } catch {
      setError("회원가입에 실패했습니다. 이미 존재하는 계정일 수 있습니다.");
    }
  };

  return { handleLogin, handleRegister, error };
};
