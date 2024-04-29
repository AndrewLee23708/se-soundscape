import './globals.css'
import 'bootstrap/dist/css/bootstrap.css'

export const metadata = {
  title: 'Soundscapes',
  description: 'Spotify IRL',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
