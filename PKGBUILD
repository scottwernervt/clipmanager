# Maintainer: Scott Werner <scott.werner.vt@gmail.com>

pkgname=clipmanager
pkgver=0.4
pkgrel=1
pkgdesc="Python Qt GUI clipboard manager"
arch=('any')
url="https://github.com/scottwernervt/clipmanager"
license=('BSD')
depends=('python2' 'python2-setuptools' 'python2-pyside' 'python2-xlib')
optdepends=('xdotool: paste into active window')
install=$pkgname.install
source=("https://github.com/scottwernervt/${pkgname}/archive/${pkgver}.tar.gz")
md5sums=('SKIP')

package() {
  cd $pkgname-$pkgver
  python2 ./setup.py install --root="$pkgdir/"
}

# vim:set ts=2 sw=2 et: