import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import {translate} from '@docusaurus/Translate';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: translate({message: '纯 Nolang 实现'}),
    description: (
      <>
        {translate({message: '全部工具使用 Nolang 语言编写，不依赖外部系统命令'})}
      </>
    ),
  },
  {
    title: translate({message: '193 个命令'}),
    description: (
      <>
        {translate({message: '单一可执行文件，子命令分发，涵盖文件、文本、压缩、系统、网络等'})}
      </>
    ),
  },
  {
    title: translate({message: '多子项目'}),
    description: (
      <>
        {translate({message: '内含 nogit（Git）、noimg（图像）、nouv（Python 包管理）、nonpm（Node.js 包管理）'})}
      </>
    ),
  },
];

function Feature({title, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
