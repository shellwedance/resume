// Injected by scripts/print_pdf.py right before Page.printToPDF.
// Adds page-break rules so the PDF splits between resume items instead of
// mid-paragraph. Rules are structural, so they keep working as content grows:
//   - each company in Work Experience starts on a new page
//   - each project block (orange h3 up to the next h3) stays on one page
//   - headings stay with the content that follows them
//   - items in Skill / Education / Recognition are not split
(() => {
  const expSection = document.querySelector('section.content-section');
  expSection.querySelectorAll('.resume-item').forEach(item => {
    let wrapper = null;
    Array.from(item.childNodes).forEach(node => {
      const isEl = node.nodeType === 1;
      if (isEl && (node.classList.contains('resume-item-title') || node.classList.contains('resume-item-details'))) return;
      if (isEl && node.tagName === 'H3') {
        wrapper = document.createElement('div');
        wrapper.className = 'sub-item';
        item.insertBefore(wrapper, node);
      }
      if (wrapper) wrapper.appendChild(node);
    });
  });

  const style = document.createElement('style');
  style.textContent = `
    .sub-item { break-inside: avoid; page-break-inside: avoid; }
    section.content-section:first-of-type .resume-item + .resume-item { break-before: page; page-break-before: always; }
    .resume-item .resume-item-title, .resume-item .resume-item-details, .section-header, h3, h4 { break-after: avoid; page-break-after: avoid; }
    section.content-section:not(:first-of-type) .resume-item { break-inside: avoid; page-break-inside: avoid; }
  `;
  document.head.appendChild(style);
  return document.querySelectorAll('.sub-item').length;
})();
