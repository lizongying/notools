import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    'intro',
    'history',
    'install',
    'tools',
    {
      type: 'category',
      label: '子项目',
      items: ['nogit', 'noimg', 'nouv', 'nonpm', 'noagent'],
    },
    {
      type: 'category',
      label: '开发指南',
      items: ['dev/build', 'dev/tests', 'dev/structure'],
    },
  ],
};

export default sidebars;
