// CSS加载检查脚本
console.log('=== CSS样式检查 ===');

// 检查CSS变量是否被定义
const root = document.documentElement;
const primaryColor = getComputedStyle(root).getPropertyValue('--color-primary');
console.log('✓ CSS变量 --color-primary:', primaryColor || '❌ 未定义');

// 检查body背景
const bodyBg = getComputedStyle(document.body).background;
console.log('✓ Body背景:', bodyBg.substring(0, 100) + '...');

// 检查.star-map-panel是否存在
setTimeout(() => {
  const panel = document.querySelector('.star-map-panel');
  if (panel) {
    console.log('✓ StarMap Panel找到');
    const panelBg = getComputedStyle(panel).background;
    const panelBorder = getComputedStyle(panel).border;
    const panelShadow = getComputedStyle(panel).boxShadow;
    console.log('  背景:', panelBg.substring(0, 100) + '...');
    console.log('  边框:', panelBorder);
    console.log('  阴影:', panelShadow.substring(0, 100) + '...');
  } else {
    console.log('❌ StarMap Panel未找到');
  }
  
  // 检查所有加载的CSS文件
  const styleSheets = Array.from(document.styleSheets);
  console.log('✓ 已加载的CSS文件数:', styleSheets.length);
  styleSheets.forEach((sheet, index) => {
    try {
      const href = sheet.href || '(inline)';
      const rules = sheet.cssRules?.length || 0;
      console.log(`  [${index}] ${href} - ${rules} rules`);
    } catch (e) {
      console.log(`  [${index}] (无法访问)`);
    }
  });
}, 1000);
