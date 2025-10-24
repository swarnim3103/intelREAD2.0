import {Link} from "react-router";
export default function Header() {
    return(
        <>
        <Link to="/dashboard"><h1 className="fixed text-4xl top-3 left-3">intel<span className="text-blue-400">Read</span>.</h1></Link>
        </>
    )
}