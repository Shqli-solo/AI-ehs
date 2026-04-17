export type DeviceStatus = "online" | "warning" | "offline";

export interface Device {
  id: string;
  name: string;
  type: string;
  location: string;
  status: DeviceStatus;
  realTimeValue: number;
  unit: string;
  thresholdHigh: number;
  thresholdLow: number;
  model: string;
  installedAt: string;
  lastCalibrated: string;
}
