import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';
import AsyncStorage from '@react-native-async-storage/async-storage';
export const BASE = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';
let token = '';
export async function setToken(value: string) {
  token=value;
  if(Platform.OS==='web') { if(value) sessionStorage.setItem('ir-token',value); else sessionStorage.removeItem('ir-token'); }
  else if(value) await SecureStore.setItemAsync('ir-token',value); else await SecureStore.deleteItemAsync('ir-token');
}
export async function restoreToken() {
  token=Platform.OS==='web' ? sessionStorage.getItem('ir-token')||'' : await SecureStore.getItemAsync('ir-token')||'';
  return token;
}
export async function api(path: string, method='GET', body?: unknown, audio?: {blob: Blob; webm: boolean}) {
  const controller=new AbortController(); const timer=setTimeout(()=>controller.abort(),90000);
  try {
    const r=await fetch(BASE+path,{method,signal:controller.signal,headers:{...(token?{Authorization:'Bearer '+token}:{}),'Content-Type':audio?'audio/octet-stream':'application/json',...(audio?{'X-Audio-Format':audio.webm?'webm':'m4a'}:{})},body:audio?audio.blob:body===undefined?undefined:JSON.stringify(body)});
    const data=await r.json(); if(!r.ok) throw new Error(data.error||'Please retry.'); return data;
  } catch(e) { if(e instanceof Error && e.name==='AbortError') throw new Error('The request timed out. Your draft is saved. Please retry.'); throw e; }
  finally {clearTimeout(timer);}
}
export async function clearDrafts() {
  const keys=(await AsyncStorage.getAllKeys()).filter(k=>k.startsWith('ir-draft:')); if(keys.length) await AsyncStorage.multiRemove(keys);
}
