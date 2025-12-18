
export const HapticService = {
  vibrate: (pattern: number | number[]) => {
    if ('vibrate' in navigator) {
      navigator.vibrate(pattern);
    }
  },
  
  capture: () => HapticService.vibrate(50),
  
  success: () => HapticService.vibrate([100, 50, 100]),
  
  danger: () => HapticService.vibrate([400, 200, 400, 200, 400]),
  
  error: () => HapticService.vibrate([50, 50, 50, 50, 50]),
  
  thinking: () => HapticService.vibrate(20)
};
