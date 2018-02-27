# Maintainer: Scott Werner <scott.werner.vt@gmail.com>
pkgname=clipmanager
pkgver=v0.4.0
pkgrel=1
pkgdesc="Python Qt GUI clipboard manager"
arch=('i686' 'x86_64')
url="https://github.com/scottwernervt/clipmanager"
license=('BSD')
depends=('python2' 'python2-setuptools' 'python2-pyside' 'python2-xlib')
optdepends=('xdotool: paste into active window')
install=$pkgname.install
source=("https://github.com/scottwernervt/${pkgname}/archive/${pkgver}.tar.gz")
md5sums=('') #autofill using updpkgsums

package() {
  cd $pkgname-$pkgver

  python2 ./setup.py install --root="$pkgdir/"
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}