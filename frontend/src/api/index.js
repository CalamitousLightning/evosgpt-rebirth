import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "https://api.evosgpt.xyz",
});

export const registerUser = (d)  => API.post("/auth/register", d);
export const loginUser    = (d)  => API.post("/auth/login", d);
export const sendMessage  = (d)  => API.post("/chat", d);
export const getMemory    = (id) => API.get(`/memory/${id}`);
export const clearMemory  = (id) => API.delete(`/memory/${id}`);
export const getUser      = (id) => API.get(`/user/${id}`);
export const initUpgrade  = (d)  => API.post("/upgrade/init", d);
export const redeemCoupon = (d)  => API.post("/coupon/redeem", d);
export const getReferral  = (id) => API.get(`/referral/${id}`);

export default API;
