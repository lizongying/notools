import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'notools',
  tagline: 'Unix 常用命令行工具集 — 纯 Nolang 实现',
  favicon: 'img/logo.svg',

  url: 'https://lizongying.github.io',
  baseUrl: '/notools/',

  organizationName: 'lizongying',
  projectName: 'notools',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'zh-Hans',
    locales: ['zh-Hans'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/lizongying/notools/tree/main/docs/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'notools',
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Docs',
        },
        {
          href: 'https://github.com/lizongying/notools',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Intro',
              to: '/docs/intro',
            },
            {
              label: '安装与使用',
              to: '/docs/install',
            },
            {
              label: '工具列表',
              to: '/docs/tools',
            },
          ],
        },
        {
          title: '子项目',
          items: [
            {
              label: 'nogit',
              to: '/docs/nogit',
            },
            {
              label: 'noimg',
              to: '/docs/noimg',
            },
            {
              label: 'nouv',
              to: '/docs/nouv',
            },
            {
              label: 'nonpm',
              to: '/docs/nonpm',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/lizongying/notools',
            },
            {
              label: 'Report Issue',
              href: 'https://github.com/lizongying/notools/issues',
            },
            {
              label: 'Nolang',
              href: 'https://github.com/lizongying/nolang',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} notools. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
